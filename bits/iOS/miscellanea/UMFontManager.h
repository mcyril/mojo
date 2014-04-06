//  ------------------------------------------------------------------------------------------------------------------------------------------------
/// @header UMFontManager.h
/// @project UnrealKit (approval pending)
/// @author Cyril Murzin
/// @copyright (c) 2014 Unreal Mojo LLC. All rights reserved.
/// @copyright (c) 2011-2014 Ravel Developer Group (Cyril Murzin). All rights reserved.
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//     __      __  ___ ___ _____.___._________
//    /  \    /  \/   |   \\__  |   |\_____   \
//    \   \/\/   /    ~    \/   |   |   /   __/
//     \        /\    Y    /\____   |  |   |
//      \__/\  /  \___|_  / / ______|  |___|
//           \/         \/  \/         <___>
//                                                                   ,,*/(((((/**.
//                                                             ./%&@@@@@@@@@@@@@@@&(/(/,.
//                                                        /#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,                        ,(%&&@&%#.
//                                                     *#@@@@@@@@@@@@@@@@@@@@@@@@@@@&@@@@@@@@@**.                 *@@@@@@@@@@@*
//                                                  .%@@@@@@@@@@@@@@@@@@@@@@@@@@&,     .,%@@@@@@&%&,               ,%@@@@@@@@@@@@/.
//                                               ./@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%     ,,  ,#@@@@@@@&(       ./%%*  /&@@@@@@@@@@@@&/
//                                              /(/(%@@@@@@@@@@@@@@@@@@@@@@@@@@@&.     *,   #@@@@@@@@&(     (&@@@@%(&@@@@@@@@@@@@@#
//                                            /%(%@@@@@@@@@@@@@@@@@@@@@@@@%(*,..            *%@@@@@@&&&.   ,#@@@@@@@@@@@@@@@@@@@&/
//                                          ,(@@@@@@@@@&&&@@@@@@@@@@@@%*,/%%&&%(          .,%@@@@@####%%*.  .&@@@@@@@@@@@@@@@@@@%,
//                                         *@@@@@@@@%.     ,%@@@@@@#*  #&&&&&&&&(          ,&@@@@&%#######%%, ./@@@@@@@@@@@@@@@@@*
//                                       ,&@@@@@@   ,,     ,@@(      %&&&&&&%(             .%@@%%#########%#.   .%@@@@@@@@@@@@@@#
//                                .*/#&@@@@@@@@@@(.   ,#,   ./#,        ,/(##/                .(@&%###########(,  *@@@@@@@@@@@@@(
//                               /,    (&@@@@@@@@*          (/                                  %@@###########%(   %@@@@@@@@@@@@/
//                              *.     (&@@@@@@@@#,       *(.                      .,,,**,,,.   ,@@&%##########%,  *%@@@@@@@@@@@/
//                              (*   ,/@@@@@@@@@@@@%(,,*/%/.                .*#%@@@@@@@@@@@%.    %@@@%%########%*  .(@@@@@@@@@@@/
//                              *@@@@@@@@@@@@@@@@@@@@@@@@%               /&@@@@@@@@@@@@@@/       #@@@@&%%######%&,  ,@@@@@@@@@@@#
//                               (&@@@@@@@@@@@@@@@@@@@@@@*           .*&@@@@@@@@@@@@@@%,         /&@@@@@@&%%%%&@@   %@@@@@@@@@@%
//                                 ,,#&@@@&%%#%%%&&@@@@@@,         /%@@@@@@@@@@@@@@#*            (@@@@@@@@@@@@@@@@@/.#@@@@@@@@@@&.
//                                   *&@##########%@@@@@,     .(%%%%%%%%##/**,                  .&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*
//                             .#@@/.*%%#############%@@@#                                      (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#,
//                            .(@@@@%,#%#############%&@@&,                                   .(@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%,
//                            ,%@@@@&,/###############%@@@%/                                .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#,
//                     ,,,..  .(@@@@&,,%##############%@@@@@#*                            ,(@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/
//                  .%@@@@@@@@%&@@@@@/,###############&@@@@@@@%/                       ,/&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,
//                 *&@@@@@@@@@@@@@@@@%*#%############&@@@@@@@@@@@%(,.            ..*(&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&.
//                 (&@@@@@@@@@@@@@@@@@@&&%#########%%@@@@@@@@@@@@@@@@@@&&%%%%%&&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%
//                 ,#@@@@@@@@@@@@@@@@@@@@@@&&%%%%&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*
//                  .&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*
//                   .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
//                      .(&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&.
//                          ..*/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(.
//                              .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
//                                .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/.
//                                 ./@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%
//                                   ,(@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&/
//                                     #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*
//                                      ,&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
//                                       .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/
//                                         .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*
//                                           ,&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
//                                            *&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(.
//                                            ,%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.
//                                            ,%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&(
//                                            ,%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/
//                                            *%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------------------------------------------------------------------------

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  The MIT License (MIT)
//
//  Copyright (c) 2014 Unreal Mojo LLC
//  Copyright (c) 2011-2014 Ravel Developer Group (Cyril Murzin)
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
/// @discussion this source aimed to search for derived typefaces' for based font
//  ------------------------------------------------------------------------------------------------------------------------------------------------

#import <UIKit/UIKit.h>

/// core class of font management utilities
@interface UMFontManager : NSObject
{
@private
    struct _manager_pvt* _private;
}

/// shared instance

+ (UMFontManager*)shared;

/// finds the italic typeface of font based on the given one
/// @param ifont used as a base font
/// @param allowLighter allows search for italic in lighter weights
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are italic typefaces (marked with italic traits) of the lighter or the same weight in the font's family

- (UIFont*)italicFontWithFont:(UIFont*)ifont allowLighter:(BOOL)allowLighter;

/// finds the weigher typeface of font based on the given one
/// @param ifont used as a base font
/// @param justWeighter forces result to first weighter typeface despite of traits
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter typefaces which have the same traits in the font's family

- (UIFont*)weighterFontWithFont:(UIFont*)ifont justWeighter:(BOOL)justWeighter;

@end

//  ------------------------------------------------------------------------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------------------------------------------------------------------------

/// UIFont extension category
@interface UIFont (MBExtensions)

/// finds the italic typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are italic typefaces (marked with italic traits) of the same weight in the font's family,
///     for relaxed search rules see UMFontManager interface
/// @see UMFontManager

+ (UIFont*)italicFontWithFont:(UIFont*)ifont;

/// finds the bold typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter bold typefaces which have the same traits in the font's family
///     if there's no bold traits of weighter typefaces, the first weighter typefaces of the same traits will be used
/// @see UMFontManager

+ (UIFont*)boldFontWithFont:(UIFont*)ifont;

/// finds the weigher typeface of font based on the given one
/// @param ifont used as a base font
/// @return instance of found font or given font if there is no candidate found
/// @discussion candidates are weighter typefaces which have the same traits in the font's family
///     it behaves like italicFontWithFont: method with relaxed search rules
/// @see UMFontManager

+ (UIFont*)weighterFontWithFont:(UIFont*)ifont;

@end

//  ------------------------------------------------------------------------------------------------------------------------------------------------
