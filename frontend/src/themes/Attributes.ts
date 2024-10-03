// Copyright (c) DAIA Tech Pvt Ltd
//
// List of theme attributes. A theme must define the colors for all these attributes

import { Colors } from '@chakra-ui/react';

export const ColorAttributes = [
  'primary',
  'primaryDark',
  'primaryBackground',
  'white',
  'black',
  'almostWhite',
  'dirtyWhite',
  'stockGray',
  'lightGray',
  'impactGreen',
  'deepSea',
  'crimsonRed',
  'techBlue',
  'skyBlue',
] as const;
export type ColorAttribute = (typeof ColorAttributes)[number];

export type KaryaColorTheme = { [key in ColorAttribute]: Colors | string };

export const ColorMap: { [key in ColorAttribute]: key } = {
  white: 'white',
  black: 'black',
  stockGray: 'stockGray',
  almostWhite: 'almostWhite',
  dirtyWhite: 'dirtyWhite',
  lightGray: 'lightGray',
  primary: 'primary',
  primaryDark: 'primaryDark',
  primaryBackground: 'primaryBackground',
  impactGreen: 'impactGreen',
  deepSea: 'deepSea',
  crimsonRed: 'crimsonRed',
  techBlue: 'techBlue',
  skyBlue: 'skyBlue',
};
