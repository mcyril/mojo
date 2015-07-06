//  ------------------------------------------------------------------------------------------------------------------------------------------------
/// @source UMFontManager.h
/// @project UnrealKit (approval pending)
/// @author Cyril Murzin
/// @copyright (c) 2014 Unreal Mojo LLC. All rights reserved.
/// @copyright (c) 2011-2014 Ravels Developer Group (Cyril Murzin). All rights reserved.
//  ------------------------------------------------------------------------------------------------------------------------------------------------

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  The MIT License (MIT)
//
//  Copyright (c) 2014 Unreal Mojo LLC
//  Copyright (c) 2011-2014 Ravel Developers Group (Cyril Murzin)
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to
//  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
//  the Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
//  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
//  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
//  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
//  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//  ------------------------------------------------------------------------------------------------------------------------------------------------

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  *** first things first

#if __has_feature(objc_arc)
#error no ARC allowed 'cause we use no ARC
#endif

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  *** includes

#import "UMFontManager.h"

#import <CoreText/CoreText.h>

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  *** forward declarations, globals and typedefs

/// I remember the times when font editors created bullshit instead of real traits and the idea to check the slant angle wasn't bad (assume it's optional in XXI century)
#define _UM_FONTMGR_CONSIDER_SLANT  0

/// 'head' table as per Microsoft TTF specification
struct _ttf_table_head
{
    uint32_t            version;
    uint32_t            fontRevision;
    uint32_t            checkSumAdjustment;
    uint32_t            magicNumber;
    uint16_t            flags;
    uint16_t            unitsPerEm;
    uint64_t            created;
    uint64_t            modified;
    int16_t             xMin;
    int16_t             yMin;
    int16_t             xMax;
    int16_t             yMax;
    uint16_t            macStyle;
    uint16_t            lowestRecPPEM;
    int16_t             fontDirectionHint;
    int16_t             indexToLocFormat;
    int16_t             glyphDataFormat;
}                                               __attribute__((packed));
typedef struct _ttf_table_head ttf_table_head_t;

/// 'OS/2' table as per Microsoft TTF specification
struct _ttf_table_os2
{
    uint16_t            version;                    /* 0x0001, table is shorten for version 0, but I don't care */
    int16_t             xAvgCharWidth;
    uint16_t            usWeightClass;
    uint16_t            usWidthClass;
    int16_t             fsType;
    int16_t         	ySubscriptXSize;
    int16_t             ySubscriptYSize;
    int16_t             ySubscriptXOffset;
    int16_t             ySubscriptYOffset;
    int16_t             ySuperscriptXSize;
    int16_t             ySuperscriptYSize;
    int16_t             ySuperscriptXOffset;
    int16_t             ySuperscriptYOffset;
    int16_t             yStrikeoutSize;
    int16_t             yStrikeoutPosition;
    int16_t             sFamilyClass;
    uint8_t             panose[10];
    uint32_t            ulUnicodeRange1;
    uint32_t            ulUnicodeRange2;
    uint32_t            ulUnicodeRange3;
    uint32_t            ulUnicodeRange4;
    int8_t              achVendID[4];
    uint16_t            fsSelection;
    uint16_t            usFirstCharIndex;
    uint16_t        	usLastCharIndex;
    uint16_t        	sTypoAscender;
    uint16_t            sTypoDescender;
    uint16_t            sTypoLineGap;
    uint16_t            usWinAscent;
    uint16_t            usWinDescent;
    uint32_t            ulCodePageRange1;
    uint32_t            ulCodePageRange2;
}                                               __attribute__((packed));
typedef struct _ttf_table_os2 ttf_table_os2_t;

/// font weights as per Microsoft TTF specification
enum _ttf_weight
{
    FW_THIN             = 100,      //  Thin
    FW_EXTRALIGHT       = 200,      //  Extra-light (Ultra-light)
    FW_LIGHT            = 300,      //  Light
    FW_NORMAL           = 400,      //  Normal (Regular)
    FW_MEDIUM           = 500,      //  Medium
    FW_SEMIBOLD         = 600,      //  Semi-bold (Demi-bold)
    FW_BOLD             = 700,      //  Bold
    FW_EXTRABOLD        = 800,      //  Extra-Bold (Ultra-bold)
    FW_BLACK            = 900       //  Black (Heavy)
};

/// font traits as per 'tx' layout engine
enum _tx_traits
{
    tx_style_plain      = 0x0000,
    tx_style_bold       = 0x0001,
    tx_style_italic     = 0x0002,
    tx_style_bolditalic = tx_style_bold|tx_style_italic,

    tx_style_expanded   = 0x0010,
    tx_style_condensed  = 0x0020,
    tx_style_light      = 0x0080
};
typedef enum _tx_traits tx_traits_t;

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  *** private classes

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  interface

/// font traits class, keeps all needed info
@interface UMFontManagerFontTraits : NSObject
{
@public
    tx_traits_t         _traits;

    uint16_t            _usWeightClass;
#if _UM_FONTMGR_CONSIDER_SLANT
    BOOL                _slanted;
#endif

@private
    NSString*           _fontName;
}
@property (nonatomic, retain) NSString* fontName;

@end

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  implementation

@implementation UMFontManagerFontTraits
@synthesize fontName = _fontName;

- (id)init
{
    self = [super init];
    if (self != nil)
    {
        _traits = tx_style_plain;

        _usWeightClass = FW_NORMAL;
#if _UM_FONTMGR_CONSIDER_SLANT
        _slanted = NO;
#endif
    }

    return self;
}

- (void)dealloc
{
    [_fontName release];

    [super dealloc];
}

#pragma mark -

- (NSString*)description
{
static NSString* const _sStyles[] = { @"plain", @"bold", @"italic", @"bold-italic" };

#if _UM_FONTMGR_CONSIDER_SLANT
    return [NSString stringWithFormat:@"%@: %@, %i, %i", _fontName, _traits <= tx_style_bolditalic ? _sStyles[_traits] : [NSNumber numberWithInt:_traits], _usWeightClass, _slanted];
#else
    return [NSString stringWithFormat:@"%@: %@, %i", _fontName, _traits <= tx_style_bolditalic ? _sStyles[_traits] : [NSNumber numberWithInt:_traits], _usWeightClass];
#endif
}

#pragma mark -

- (NSComparisonResult)compare:(UMFontManagerFontTraits*)entity
{
    if (_usWeightClass < entity->_usWeightClass)
        return NSOrderedAscending;
    else if (_usWeightClass > entity->_usWeightClass)
        return NSOrderedDescending;
    else
    {
        if (_traits < entity->_traits)
            return NSOrderedAscending;
        else if (_traits > entity->_traits)
            return NSOrderedDescending;
    }

    return NSOrderedSame;
}

@end

#pragma mark -
#pragma mark -
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  *** core classes

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  forward declarations, globals and typedefs

/// instance
static UMFontManager*       sFontManager = nil;

///
static NSString* const      kSentinelString = @"--###SENTINEL###--";

/// private data storage
struct _manager_pvt
{
    NSArray*                system_families;

    NSMutableDictionary*    families_pool;
    NSMutableDictionary*    families_fallback;

    NSMutableDictionary*    fonts_pool;
    NSMutableDictionary*    fonts_variations;   // TODO: cache found associations and candidates
};
typedef struct _manager_pvt manager_pvt_t;

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  private interface

@interface UMFontManager ()
- (UMFontManagerFontTraits*)_collectPoolRecord:(NSString*)fontName;
- (UMFontManagerFontTraits*)_fontPoolRecord:(NSString*)fontName;

- (NSDictionary*)_collectFamilyPool:(NSString*)familyName;
- (NSDictionary*)_familyPool:(NSString*)familyName;
@end

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  implementation

@implementation UMFontManager

- (id)init
{
    self = [super init];
    if (self != nil)
    {
        _private = (manager_pvt_t*)malloc(sizeof(manager_pvt_t));

        // NOTE: stored in specific order for fallback algo
        _private->system_families = [[[UIFont familyNames] sortedArrayUsingComparator:^NSComparisonResult(NSString* fam1, NSString* fam2)
                                                                      {
                                                                          NSUInteger len1 = [fam1 length];
                                                                          NSUInteger len2 = [fam2 length];

                                                                          if (len1 > len2)
                                                                              return NSOrderedAscending;
                                                                          else if (len1 < len2)
                                                                              return NSOrderedDescending;
                                                                          else
                                                                              return [fam2 compare:fam1];
                                                                      }] retain];

        _private->families_pool = [[NSMutableDictionary alloc] initWithCapacity:0];
        _private->families_fallback = [[NSMutableDictionary alloc] initWithCapacity:0];

        _private->fonts_pool = [[NSMutableDictionary alloc] initWithCapacity:0];
        _private->fonts_variations = [[NSMutableDictionary alloc] initWithCapacity:0];
    }

    return self;
}

- (void)dealloc
{
    [_private->system_families release];

    [_private->families_pool release];
    [_private->families_fallback release];

    [_private->fonts_pool release];
    [_private->fonts_variations release];

    free(_private);

    [super dealloc];
}

+ (UMFontManager*)shared
{
    if (sFontManager == nil)
    {
    static dispatch_once_t _once;

        dispatch_once(&_once, ^
                        {
                            sFontManager = [[UMFontManager alloc] init];
                        });
    }

    return sFontManager;
}

#pragma mark -
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  private interface

/// create family pool record for certain font name
/// @param fontName the name of font
/// @return typeface traits
/// @discussion creates pool record on demand with _collectPoolRecord: method

- (UMFontManagerFontTraits*)_collectPoolRecord:(NSString*)fontName
{
    UMFontManagerFontTraits* entity = [[[UMFontManagerFontTraits alloc] init] autorelease];

    CTFontRef font = CTFontCreateWithName((CFStringRef)fontName, .0, NULL);
    if (font != NULL)
    {
    // deal with CoreText information

    // collect regular traits

        CTFontSymbolicTraits symTraits = CTFontGetSymbolicTraits(font);

        if ((symTraits & kCTFontTraitBold) != 0)
            entity->_traits |= tx_style_bold;
        if ((symTraits & kCTFontTraitItalic) != 0)
            entity->_traits |= tx_style_italic;
        if ((symTraits & kCTFontTraitCondensed) != 0)   //  adding of condensed traits will exclude this styles from findings; TODO: some fallback for them though?
            entity->_traits |= tx_style_condensed;
        if ((symTraits & kCTFontTraitExpanded) != 0)    //  adding of expanded traits will exclude this styles from findings; TODO: some fallback for them though?
            entity->_traits |= tx_style_expanded;

    // collect weight

        CFDataRef ttfOS2Table = CTFontCopyTable(font, kCTFontTableOS2, kCTFontTableOptionNoOptions);
        if (ttfOS2Table != NULL)
        {
            ttf_table_os2_t* os2table = (ttf_table_os2_t*)CFDataGetBytePtr(ttfOS2Table);

            entity->_usWeightClass = OSSwapBigToHostInt16(os2table->usWeightClass);

            CFRelease(ttfOS2Table);
        }

    // italic hint

#if _UM_FONTMGR_CONSIDER_SLANT
        CGFloat slant = CTFontGetSlantAngle(font);

        entity->_slanted = (fabsf(slant) > .0);
#endif

        CFRelease(font);
    }
    else
    {
    // guess with name

    // collect regular traits

        if ([fontName rangeOfString:@"bold" options:NSCaseInsensitiveSearch].length > 0 ||
            [fontName rangeOfString:@"black" options:NSCaseInsensitiveSearch].length > 0)
            entity->_traits |= tx_style_bold;
        if ([fontName rangeOfString:@"italic" options:NSCaseInsensitiveSearch].length > 0 ||
            [fontName rangeOfString:@"oblique" options:NSCaseInsensitiveSearch].length > 0)
            entity->_traits |= tx_style_italic;
        if ([fontName rangeOfString:@"condensed" options:NSCaseInsensitiveSearch].length > 0)
            entity->_traits |= tx_style_condensed;
        if ([fontName rangeOfString:@"expanded" options:NSCaseInsensitiveSearch].length > 0)
            entity->_traits |= tx_style_expanded;

    // collect weight

        CGFontRef font = CGFontCreateWithFontName((CFStringRef)fontName);
        if (font != NULL)
        {
            CFDataRef ttfOS2Table = CGFontCopyTableForTag(font, os2FontTableTag);
            if (ttfOS2Table != NULL)
            {
                ttf_table_os2_t* os2table = (ttf_table_os2_t*)CFDataGetBytePtr(ttfOS2Table);

                entity->_usWeightClass = OSSwapBigToHostInt16(os2table->usWeightClass);

                CFRelease(ttfOS2Table);
            }

    // italic hint

#if _UM_FONTMGR_CONSIDER_SLANT
            CGFloat slant = CGFontGetItalicAngle(font);

            entity->_slanted = (fabsf(slant) > .0);
#endif

            CGFontRelease(font);
        }
    }

    entity.fontName = fontName;

    return entity;
}

/// retrieve family pool record for certain font name
/// @param fontName the name of font
/// @return typeface traits
/// @discussion creates pool record on demand with _collectPoolRecord: method

- (UMFontManagerFontTraits*)_fontPoolRecord:(NSString*)fontName
{
    @synchronized(_private->fonts_pool)
    {
        UMFontManagerFontTraits* entity = [_private->fonts_pool objectForKey:fontName];
        if (entity == nil)
        {
            entity = [self _collectPoolRecord:fontName];

            [_private->fonts_pool setObject:entity forKey:fontName];
        }

        return entity;
    }
}

/// create family pool for certain family name and collect all typefaces info
/// @param familyName the name of font family
/// @return collection of typefaces' traits which belong to family

- (NSDictionary*)_collectFamilyPool:(NSString*)familyName
{
    NSMutableDictionary* familyPool = [NSMutableDictionary dictionaryWithCapacity:0];

    NSArray* fontNames = [UIFont fontNamesForFamilyName:familyName];
    for (NSString* fontName in fontNames)
    {
        [familyPool setObject:[self _fontPoolRecord:fontName] forKey:fontName];
    }

    // do not propagate empty dictionary, it could happen if font family is synthesized
    // despite _familyPool: should care of it, let's just to be on the safe side
    return [familyPool count] > 0 ? familyPool : nil;
}

/// retrieve family pool for certain family name
/// @param familyName the name of font family
/// @return collection of typefaces' traits which belong to family
/// @discussion creates pool on demand with _collectFamilyPool: method

- (NSDictionary*)_familyPool:(NSString*)familyName
{
    @synchronized(_private->families_pool)
    {
        NSDictionary* familyPool = [_private->families_pool objectForKey:familyName];
        while (familyPool == nil)
        {
            NSString* actualFamilyName = [_private->families_fallback objectForKey:familyName];
            if (actualFamilyName != nil)
            {
            // assume we've already registered pool when did fallback, so get it and bail out
            // it's possible there is no pool for questionable family if it failed on fallback

                familyPool = [_private->families_pool objectForKey:actualFamilyName];
                break;
            }

            // still no pool or fallback, check if family exists in system

            NSString* targetFamilyName = familyName;
            if ([_private->system_families indexOfObject:targetFamilyName] == NSNotFound)
            {
            // no family in system, perform poor attempt of fallback

                // NOTE: strip leading dot for synthesized system fonts
                if ([targetFamilyName hasPrefix:@"."])
                    targetFamilyName = [targetFamilyName substringFromIndex:1];

                for (NSString* candidate in _private->system_families)
                    if ([targetFamilyName hasPrefix:candidate])
                    {
                    // most reasonable family name
                        actualFamilyName = candidate;
                        break;
                    }

                if (actualFamilyName == nil)
                {
                // found nothing, so register fake fallback for further bypassing and bail out

                    [_private->families_fallback setObject:kSentinelString forKey:familyName];
                    break;
                }

                // register fallback candidate and deal with it instead of actual family
                [_private->families_fallback setObject:actualFamilyName forKey:familyName];

                // it's possible that fallback already in pool, bail out if it's so
                familyPool = [_private->families_pool objectForKey:actualFamilyName];
                if (familyPool != nil)
                    break;

            // else deal with fallback family name
            }
            else
            {
            // straight case, deal with desired family name

                actualFamilyName = familyName;
            }

            familyPool = [self _collectFamilyPool:actualFamilyName];
            if (familyPool == nil)
            {
            // impossible to collect any information on desired family name, so register fake fallback for further bypassing

                [_private->families_fallback setObject:kSentinelString forKey:familyName];
            }
            else
            {
            // register collected pool

                [_private->families_pool setObject:familyPool forKey:familyName];
            }

            // finally
            break;
        }

        return familyPool;
    }
}

#pragma mark -
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  public interface

/// finds the italic typeface of font based on the given one
/// @param ifont used as a base font
/// @param allowLighter allows search for italic in lighter weights
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are italic typefaces (marked with italic traits) of the lighter or the same weight in the font's family

- (UIFont*)italicFontWithFont:(UIFont*)ifont allowLighter:(BOOL)allowLighter
{
    UIFont* font = ifont;

    if (font != nil)
    {
        UMFontManagerFontTraits* originalEntity = [self _fontPoolRecord:ifont.fontName];
        if (originalEntity != nil)
        {
            tx_traits_t original_traits = originalEntity->_traits;
            tx_traits_t wanted_traits = original_traits | tx_style_italic;

            if (wanted_traits == originalEntity->_traits)
            {
            // already italic? don't fool with me!

                return font;
            }

#if _UM_FONTMGR_CONSIDER_SLANT
            if (originalEntity->_slanted)
            {
            // slanted? don't fool with me!

                return font;
            }
#endif

            __block NSDictionary* familyPool = [self _familyPool:ifont.familyName];
            if (familyPool != nil)
            {
                NSArray* sortedKeys = [[familyPool allKeys] sortedArrayUsingComparator:^NSComparisonResult(NSString* nam1, NSString* nam2)
                                                                {
                                                                    UMFontManagerFontTraits* ent1 = [familyPool objectForKey:nam1];
                                                                    UMFontManagerFontTraits* ent2 = [familyPool objectForKey:nam2];

                                                                    return [ent1 compare:ent2];
                                                                }];

                // search for first occurence of font which weight same as original

                NSUInteger index = 0;
                NSUInteger icount = [sortedKeys count];
                for (NSString* key in sortedKeys)
                {
                    UMFontManagerFontTraits* foundEntity = [familyPool objectForKey:key];

                    if (foundEntity->_usWeightClass == originalEntity->_usWeightClass)
                        break;
                    else
                        index++;
                }

                NSUInteger first_italic = NSNotFound;

                if (index < icount)
                {
                // found watermark

                    for ( ; index < icount; index++)
                    {
                        UMFontManagerFontTraits* entity = [familyPool objectForKey:[sortedKeys objectAtIndex:index]];

#if _UM_FONTMGR_CONSIDER_SLANT
                        BOOL ok = (((entity->_traits == wanted_traits) || (entity->_traits == original_traits && entity->_slanted)) && entity->_usWeightClass == originalEntity->_usWeightClass);
#else
                        BOOL ok = (entity->_traits == wanted_traits && entity->_usWeightClass == originalEntity->_usWeightClass);
#endif
                        if (ok)
                        {
                            first_italic = index;
                            break;
                        }
                    }

                    if (first_italic == NSNotFound)
                        goto try_lighter;
                    else
                        index = first_italic;
                }
                else
                {
                // no font with the same weight, so nothing to do...

                try_lighter:;

                // could be stupid idea, though why not to find lighter italic variant?

                    if (allowLighter)
                    {
                        index = icount;

                        do
                        {
                            index--;

                            UMFontManagerFontTraits* entity = [familyPool objectForKey:[sortedKeys objectAtIndex:index]];

#if _UM_FONTMGR_CONSIDER_SLANT
                            BOOL ok = (((entity->_traits == wanted_traits) || (entity->_traits == original_traits && entity->_slanted)) && entity->_usWeightClass < originalEntity->_usWeightClass);
#else
                            BOOL ok = (entity->_traits == wanted_traits && entity->_usWeightClass < originalEntity->_usWeightClass);
#endif
                            if (ok)
                            {
                                first_italic = index;
                                break;
                            }

                        } while (index != 0);

                        index = first_italic;
                    }
                    else
                        index = NSNotFound;
                }

                if (index != NSNotFound)
                {
                    UMFontManagerFontTraits* entity = [familyPool objectForKey:[sortedKeys objectAtIndex:index]];

                    font = [UIFont fontWithName:entity.fontName size:ifont.pointSize];
                }
            }
        }
    }

    return font;
}

/// finds the weigher typeface of font based on the given one
/// @param ifont used as a base font
/// @param justWeighter forces result to first weighter typeface despite of traits
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter typefaces which have the same traits in the font's family

- (UIFont*)weighterFontWithFont:(UIFont*)ifont justWeighter:(BOOL)justWeighter
{
    UIFont* font = ifont;

    if (font != nil)
    {
        UMFontManagerFontTraits* originalEntity = [self _fontPoolRecord:ifont.fontName];
        if (originalEntity != nil)
        {
            __block NSDictionary* familyPool = [self _familyPool:ifont.familyName];
            if (familyPool != nil)
            {
                NSArray* sortedKeys = [[familyPool allKeys] sortedArrayUsingComparator:^NSComparisonResult(NSString* nam1, NSString* nam2)
                                                                {
                                                                    UMFontManagerFontTraits* ent1 = [familyPool objectForKey:nam1];
                                                                    UMFontManagerFontTraits* ent2 = [familyPool objectForKey:nam2];

                                                                    return [ent1 compare:ent2];
                                                                }];

                tx_traits_t original_traits = originalEntity->_traits;
                tx_traits_t wanted_traits = original_traits | tx_style_bold;

                justWeighter = justWeighter || (wanted_traits == original_traits);

                // search for first occurence of font which weight greater than original

                NSUInteger index = 0;
                NSUInteger icount = [sortedKeys count];
                for (NSString* key in sortedKeys)
                {
                    UMFontManagerFontTraits* foundEntity = [familyPool objectForKey:key];

                    if (foundEntity->_usWeightClass > originalEntity->_usWeightClass)
                        break;
                    else
                        index++;
                }

                NSUInteger first_weighter = NSNotFound;
                NSUInteger first_bolded = NSNotFound;

                if (index < icount)
                {
                // found watermark

                    for ( ; index < icount; index++)
                    {
                        UMFontManagerFontTraits* entity = [familyPool objectForKey:[sortedKeys objectAtIndex:index]];

                        if (entity->_traits == original_traits && first_weighter == NSNotFound)
                            first_weighter = index;

                        if (entity->_traits == wanted_traits && first_bolded == NSNotFound)
                            first_bolded = index;

                        if (justWeighter && first_weighter != NSNotFound)
                            break;
                        else if (first_bolded != NSNotFound)
                            break;
                    }

                    if (justWeighter)
                        index = MIN(first_weighter, first_bolded);
                    else
                    {
                        index = first_bolded;
                        if (index == NSNotFound)
                            index = first_weighter;
                    }
                }
                else
                {
                // no weighter font, so nothing to do...

                    index = NSNotFound;
                }

                if (index != NSNotFound)
                {
                    UMFontManagerFontTraits* entity = [familyPool objectForKey:[sortedKeys objectAtIndex:index]];

                    font = [UIFont fontWithName:entity.fontName size:ifont.pointSize];
                }
            }
        }
    }

    return font;
}

@end

#pragma mark -
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  fooling around (Kumamon agrees)

static void __attribute__((destructor)) __finalize()
{
    [sFontManager release];
    sFontManager = nil;
}

#pragma mark -
#pragma mark -
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  UIFont extension category methods which utilize UMFontManager

@implementation UIFont (UMTouchUIFontAdditions)

/// finds the italic typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are italic typefaces (marked with italic traits) of the same weight in the font's family,
///     for relaxed search rules see UMFontManager interface
/// @see UMFontManager

+ (UIFont*)italicFontWithFont:(UIFont*)ifont
{
    return [[UMFontManager shared] italicFontWithFont:ifont allowLighter:NO];
}

/// finds the bold typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter bold typefaces which have the same traits in the font's family
///     if there's no bold traits of weighter typefaces, the first weighter typefaces of the same traits will be used
/// @see UMFontManager

+ (UIFont*)boldFontWithFont:(UIFont*)ifont
{
    return [[UMFontManager shared] weighterFontWithFont:ifont justWeighter:NO];
}

/// finds the weigher typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter typefaces which have the same traits in the font's family
///     it behaves like italicFontWithFont: method with relaxed search rules
/// @see UMFontManager

+ (UIFont*)weighterFontWithFont:(UIFont*)ifont
{
    return [[UMFontManager shared] weighterFontWithFont:ifont justWeighter:YES];
}

@end

//  ------------------------------------------------------------------------------------------------------------------------------------------------
