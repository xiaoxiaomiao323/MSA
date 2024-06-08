 /*************************************/
 /* file strmacs.h                    */
 /* some new string macros:           */
 /*  streq(cs,ct)                     */
 /*  streqi(cs,ct)                    */
 /*  str_less_than(cs,ct)             */
 /*  str_greater_than(cs,ct)          */
 /* and some fixes for sys macros:    */
 /*  toupper(_c)                      */
 /*  tolower(_c)                      */
 /*************************************/
#ifndef STRMACS_HEADER
#define STRMACS_HEADER

#if defined (HAVE_STRCMPI) || defined (COMPILE_OWN_STRCMPI)
#   define strcasecmp strcmpi
#   define strncasecmp strncmpi
#elif defined (__WIN32__) || defined(WIN32)
#   define snprintf _snprintf
#   define strcasecmp stricmp
#   define strncasecmp strnicmp
#endif

#define streq(cs,ct)            (strcmp(cs,ct)  == 0)
#define strcaseeq(cs,ct)        (strcasecmp(cs,ct) == 0)
#define str_less_than(cs,ct)    (strcmp(cs,ct)  <  0) 
#define str_greater_than(cs,ct) (strcmp(cs,ct)  >  0) 
/* these not needed in SUN 4.1 as of 4/1/91:  */
/*
#define toupper(_c) (((_c >= 'a') && (_c <= 'z')) ? ((_c)-'a'+'A') : (_c))
#define tolower(_c) (((_c >= 'A') && (_c <= 'Z')) ? ((_c)-'A'+'a') : (_c))
*/

#endif
