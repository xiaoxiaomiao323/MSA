/*
 * ASCLITE
 * Author: Jerome Ajot, Jon Fiscus, Nicolas Radde, Chris Laprun
 *
 * This software was developed at the National Institute of Standards and Technology by 
 * employees of the Federal Government in the course of their official duties. Pursuant
 * to title 17 Section 105 of the United States Code this software is not subject to
 * copyright protection and is in the public domain. ASCLITE is an experimental system.
 * NIST assumes no responsibility whatsoever for its use by other parties, and makes no
 * guarantees, expressed or implied, about its quality, reliability, or any other
 * characteristic. We would appreciate acknowledgement if the software is used.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS."  With regard to this software, NIST MAKES NO EXPRESS
 * OR IMPLIED WARRANTY AS TO ANY MATTER WHATSOEVER, INCLUDING MERCHANTABILITY,
 * OR FITNESS FOR A PARTICULAR PURPOSE.
 */

#ifndef TEST_TRNTRN_SEGMENTOR_H
#define TEST_TRNTRN_SEGMENTOR_H

#include "trntrn_segmentor.h"

/**
 * Test the TRN to TRN segmentor.
 */
class TRNTRNSegmentorTest
{
	public:
		// class constructor
		TRNTRNSegmentorTest();
		// class destructor
		~TRNTRNSegmentorTest();
		/**
		 * Launch all the tests on the TRN to TRN segmentor
		 */
		void testAll();
		/**
		 * Test the case where the segmentor need to align 2 segments to
		 * 2 segments.
		 */
		void test2segmentsCase();
		/*
		* Test the case where the segmentor need to align 4 segments to
		* 4 segments. there are affected to 2 different speakers
		*/
		void test4segments2spkrCase();
};

#endif // TEST_TRNTRN_SEGMENTOR_H
