
from collections import OrderedDict

import torch, torchaudio
import torch.nn as nn
import torch.nn.functional as F

def get_nonlinear(config_str, channels):
    nonlinear = nn.Sequential()
    for name in config_str.split('-'):
        if name == 'relu':
            nonlinear.add_module('relu', nn.ReLU(inplace=True))
        elif name == 'prelu':
            nonlinear.add_module('prelu', nn.PReLU(channels))
        elif name == 'batchnorm':
            nonlinear.add_module('batchnorm', nn.BatchNorm1d(channels))
        elif name == 'batchnorm_':
            nonlinear.add_module('batchnorm',
                                 nn.BatchNorm1d(channels, affine=False))
        else:
            raise ValueError('Unexpected module ({}).'.format(name))
    return nonlinear


class TDNNLayer(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 dilation=1,
                 bias=False,
                 config_str='batchnorm-relu'):
        super(TDNNLayer, self).__init__()
        if padding < 0:
            assert kernel_size % 2 == 1, 'Expect equal paddings, \
                    but got even kernel size ({})'.format(kernel_size)
            padding = (kernel_size - 1) // 2 * dilation
        self.linear = nn.Conv1d(in_channels,
                                out_channels,
                                kernel_size,
                                stride=stride,
                                padding=padding,
                                dilation=dilation,
                                bias=bias)
        self.nonlinear = get_nonlinear(config_str, out_channels)

    def forward(self, x):
        x = self.linear(x)
        x = self.nonlinear(x)
        return x


class CAMLayer(nn.Module):
    def __init__(self,
                 bn_channels,
                 out_channels,
                 kernel_size,
                 stride,
                 padding,
                 dilation,
                 bias,
                 reduction=2):
        super(CAMLayer, self).__init__()
        self.linear_local = nn.Conv1d(bn_channels,
                                      out_channels,
                                      kernel_size,
                                      stride=stride,
                                      padding=padding,
                                      dilation=dilation,
                                      bias=bias)
        self.linear1 = nn.Conv1d(bn_channels, bn_channels // reduction, 1)
        self.relu = nn.ReLU(inplace=True)
        self.linear2 = nn.Conv1d(bn_channels // reduction, out_channels, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        y = self.linear_local(x)
        context = x.mean(-1, keepdim=True) + self.seg_pooling(x)
        context = self.relu(self.linear1(context))
        m = self.sigmoid(self.linear2(context))
        return y * m

    def seg_pooling(self, x, seg_len: int = 100, stype: str = 'avg'):
        if stype == 'avg':
            seg = F.avg_pool1d(x,
                               kernel_size=seg_len,
                               stride=seg_len,
                               ceil_mode=True)
        elif stype == 'max':
            seg = F.max_pool1d(x,
                               kernel_size=seg_len,
                               stride=seg_len,
                               ceil_mode=True)
        else:
            raise ValueError('Wrong segment pooling type.')
        shape = seg.shape
        seg = seg.unsqueeze(-1).expand(shape[0], shape[1], shape[2],
                                       seg_len).reshape(shape[0], shape[1], -1)
        seg = seg[..., :x.shape[-1]]
        return seg


class CAMDenseTDNNLayer(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 bn_channels,
                 kernel_size,
                 stride=1,
                 dilation=1,
                 bias=False,
                 config_str='batchnorm-relu'):
        super(CAMDenseTDNNLayer, self).__init__()
        assert kernel_size % 2 == 1, 'Expect equal paddings, \
                but got even kernel size ({})'.format(kernel_size)
        padding = (kernel_size - 1) // 2 * dilation
        self.nonlinear1 = get_nonlinear(config_str, in_channels)
        self.linear1 = nn.Conv1d(in_channels, bn_channels, 1, bias=False)
        self.nonlinear2 = get_nonlinear(config_str, bn_channels)
        self.cam_layer = CAMLayer(bn_channels,
                                  out_channels,
                                  kernel_size,
                                  stride=stride,
                                  padding=padding,
                                  dilation=dilation,
                                  bias=bias)

    def bn_function(self, x):
        return self.linear1(self.nonlinear1(x))

    def forward(self, x):
        x = self.bn_function(x)
        x = self.cam_layer(self.nonlinear2(x))
        return x


class CAMDenseTDNNBlock(nn.ModuleList):
    def __init__(self,
                 num_layers,
                 in_channels,
                 out_channels,
                 bn_channels,
                 kernel_size,
                 stride=1,
                 dilation=1,
                 bias=False,
                 config_str='batchnorm-relu'):
        super(CAMDenseTDNNBlock, self).__init__()
        for i in range(num_layers):
            layer = CAMDenseTDNNLayer(in_channels=in_channels +
                                      i * out_channels,
                                      out_channels=out_channels,
                                      bn_channels=bn_channels,
                                      kernel_size=kernel_size,
                                      stride=stride,
                                      dilation=dilation,
                                      bias=bias,
                                      config_str=config_str)
            self.add_module('tdnnd%d' % (i + 1), layer)

    def forward(self, x):
        for layer in self:
            x = torch.cat([x, layer(x)], dim=1)
        return x


class TransitLayer(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 bias=True,
                 config_str='batchnorm-relu'):
        super(TransitLayer, self).__init__()
        self.nonlinear = get_nonlinear(config_str, in_channels)
        self.linear = nn.Conv1d(in_channels, out_channels, 1, bias=bias)

    def forward(self, x):
        x = self.nonlinear(x)
        x = self.linear(x)
        return x


class DenseLayer(nn.Module):
    def __init__(self,
                 in_channels,
                 out_channels,
                 bias=False,
                 config_str='batchnorm-relu'):
        super(DenseLayer, self).__init__()
        self.linear = nn.Conv1d(in_channels, out_channels, 1, bias=bias)
        self.nonlinear = get_nonlinear(config_str, out_channels)

    def forward(self, x):
        if len(x.shape) == 2:
            x = self.linear(x.unsqueeze(dim=-1)).squeeze(dim=-1)
        else:
            x = self.linear(x)
        x = self.nonlinear(x)
        return x


'''Note: The stride used here is different from that in Resnet
'''
class BasicResBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super(BasicResBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes,
                               planes,
                               kernel_size=3,
                               stride=(stride, 1),
                               padding=1,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes,
                               planes,
                               kernel_size=3,
                               stride=1,
                               padding=1,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes,
                          self.expansion * planes,
                          kernel_size=1,
                          stride=(stride, 1),
                          bias=False),
                nn.BatchNorm2d(self.expansion * planes))

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


class FCM(nn.Module):
    def __init__(self,
                 block,
                 num_blocks,
                 m_channels=32,
                 feat_dim=80):
        super(FCM, self).__init__()
        self.in_planes = m_channels
        self.conv1 = nn.Conv2d(1,
                               m_channels,
                               kernel_size=3,
                               stride=1,
                               padding=1,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(m_channels)

        self.layer1 = self._make_layer(block,
                                       m_channels,
                                       num_blocks[0],
                                       stride=2)
        self.layer2 = self._make_layer(block,
                                       m_channels,
                                       num_blocks[0],
                                       stride=2)

        self.conv2 = nn.Conv2d(m_channels,
                               m_channels,
                               kernel_size=3,
                               stride=(2, 1),
                               padding=1,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(m_channels)
        self.out_channels = m_channels * (feat_dim // 8)

    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        x = x.unsqueeze(1)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = F.relu(self.bn2(self.conv2(out)))

        shape = out.shape
        out = out.reshape(shape[0], shape[1] * shape[2], shape[3])
        return out

class TSTP(nn.Module):
    """
    Temporal statistics pooling, concatenate mean and std, which is used in
    x-vector
    Comment: simple concatenation can not make full use of both statistics
    """

    def __init__(self, in_dim=0, **kwargs):
        super(TSTP, self).__init__()
        self.in_dim = in_dim

    def forward(self, x):
        # The last dimension is the temporal axis
        pooling_mean = x.mean(dim=-1)
        pooling_std = torch.sqrt(torch.var(x, dim=-1) + 1e-7)
        pooling_mean = pooling_mean.flatten(start_dim=1)
        pooling_std = pooling_std.flatten(start_dim=1)
        stats = torch.cat((pooling_mean, pooling_std), 1)
        return stats

    def get_out_dim(self):
        self.out_dim = self.in_dim * 2
        return self.out_dim
    
class PreEmphasis(torch.nn.Module):

    def __init__(self, coef: float = 0.97):
        super().__init__()
        self.coef = coef
        self.register_buffer(
            'flipped_filter', torch.FloatTensor([-self.coef, 1.]).unsqueeze(0).unsqueeze(0)
        )

    def forward(self, input: torch.tensor) -> torch.tensor:
        input = input.unsqueeze(1)
        input = F.pad(input, (1, 0), 'reflect')
        return F.conv1d(input, self.flipped_filter).squeeze(1)
    
class CAMPPlus(nn.Module):
    def __init__(self,
                 feat_dim=80,
                 embed_dim=512,
                 pooling_func='TSTP',
                 growth_rate=32,
                 bn_size=4,
                 init_channels=128,
                 config_str='batchnorm-relu'):
        super(CAMPPlus, self).__init__()

        self.torchfbank = torch.nn.Sequential(
            PreEmphasis(),            
            torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_fft=512, win_length=400, hop_length=160, \
                                                 f_min = 20, f_max = 7600, window_fn=torch.hamming_window, n_mels=80),
            )
        
        self.head = FCM(block=BasicResBlock, num_blocks=[2, 2], feat_dim=feat_dim)
        channels = self.head.out_channels

        self.xvector = nn.Sequential(
            OrderedDict([
                ('tdnn',
                 TDNNLayer(channels,
                           init_channels,
                           5,
                           stride=2,
                           dilation=1,
                           padding=-1,
                           config_str=config_str)),
            ]))
        channels = init_channels
        for i, (num_layers, kernel_size,
                dilation) in enumerate(zip((12, 24, 16), (3, 3, 3),
                                           (1, 2, 2))):
            block = CAMDenseTDNNBlock(num_layers=num_layers,
                                      in_channels=channels,
                                      out_channels=growth_rate,
                                      bn_channels=bn_size * growth_rate,
                                      kernel_size=kernel_size,
                                      dilation=dilation,
                                      config_str=config_str)
            self.xvector.add_module('block%d' % (i + 1), block)
            channels = channels + num_layers * growth_rate
            self.xvector.add_module(
                'transit%d' % (i + 1),
                TransitLayer(channels,
                             channels // 2,
                             bias=False,
                             config_str=config_str))
            channels //= 2

        self.xvector.add_module('out_nonlinear',
                                get_nonlinear(config_str, channels))

        self.pool = TSTP(in_dim=channels)
        self.pool_out_dim = self.pool.get_out_dim()
        self.xvector.add_module('stats', self.pool)
        self.xvector.add_module(
            'dense',
            DenseLayer(self.pool_out_dim, embed_dim, config_str='batchnorm_'))

        for m in self.modules():
            if isinstance(m, (nn.Conv1d, nn.Linear)):
                nn.init.kaiming_normal_(m.weight.data)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x):
        with torch.no_grad():
            with torch.cuda.amp.autocast(enabled=False): 
                x = self.torchfbank(x)+1e-6
                x = x.log()   
                x = x - torch.mean(x, dim=-1, keepdim=True)

        # x = x.permute(0, 2, 1)  # (B,T,F) => (B,F,T)
        x = self.head(x)
        x = self.xvector(x)
        return x
