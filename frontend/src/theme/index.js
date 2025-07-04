// Color palette
export const colors = {
  // Primary colors
  primary: '#3498DB',
  primaryDark: '#2980B9',
  primaryLight: '#85C1E9',
  
  // Secondary colors
  secondary: '#E74C3C',
  secondaryDark: '#C0392B',
  secondaryLight: '#F1948A',
  
  // Success colors
  success: '#27AE60',
  successDark: '#1E8449',
  successLight: '#82E5AA',
  
  // Warning colors
  warning: '#F39C12',
  warningDark: '#D68910',
  warningLight: '#F8C471',
  
  // Error colors
  error: '#E74C3C',
  errorDark: '#C0392B',
  errorLight: '#F1948A',
  
  // Neutral colors
  text: '#2C3E50',
  textSecondary: '#7F8C8D',
  textLight: '#95A5A6',
  textMuted: '#BDC3C7',
  
  // Background colors
  background: '#F8F9FA',
  backgroundSecondary: '#FFFFFF',
  backgroundTertiary: '#ECF0F1',
  
  // Border colors
  border: '#E1E8ED',
  borderLight: '#F4F6FA',
  borderDark: '#BDC3C7',
  
  // Overlay colors
  overlay: 'rgba(44, 62, 80, 0.5)',
  overlayLight: 'rgba(44, 62, 80, 0.2)',
  
  // Special colors
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
};

// Typography
export const typography = {
  // Font families
  fontFamily: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
  },
  
  // Font sizes
  fontSize: {
    xs: 10,
    sm: 12,
    base: 14,
    lg: 16,
    xl: 18,
    '2xl': 20,
    '3xl': 24,
    '4xl': 28,
    '5xl': 32,
    '6xl': 36,
  },
  
  // Font weights
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  
  // Line heights
  lineHeight: {
    tight: 1.2,
    normal: 1.4,
    relaxed: 1.6,
    loose: 1.8,
  },
};

// Spacing
export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  '3xl': 32,
  '4xl': 40,
  '5xl': 48,
  '6xl': 64,
};

// Border radius
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 6,
  lg: 8,
  xl: 12,
  '2xl': 16,
  '3xl': 24,
  full: 9999,
};

// Shadows
export const shadows = {
  sm: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lg: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
  xl: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
};

// Component styles
export const components = {
  // Button styles
  button: {
    primary: {
      backgroundColor: colors.primary,
      borderRadius: borderRadius.lg,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      ...shadows.md,
    },
    secondary: {
      backgroundColor: colors.background,
      borderRadius: borderRadius.lg,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      borderWidth: 1,
      borderColor: colors.border,
    },
    success: {
      backgroundColor: colors.success,
      borderRadius: borderRadius.lg,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      ...shadows.md,
    },
    warning: {
      backgroundColor: colors.warning,
      borderRadius: borderRadius.lg,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      ...shadows.md,
    },
    error: {
      backgroundColor: colors.error,
      borderRadius: borderRadius.lg,
      paddingVertical: spacing.md,
      paddingHorizontal: spacing.xl,
      ...shadows.md,
    },
  },
  
  // Input styles
  input: {
    default: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: borderRadius.lg,
      paddingHorizontal: spacing.lg,
      paddingVertical: spacing.md,
      fontSize: typography.fontSize.lg,
      backgroundColor: colors.backgroundSecondary,
    },
    focused: {
      borderColor: colors.primary,
    },
    error: {
      borderColor: colors.error,
    },
  },
  
  // Card styles
  card: {
    default: {
      backgroundColor: colors.backgroundSecondary,
      borderRadius: borderRadius.xl,
      padding: spacing.xl,
      ...shadows.md,
    },
    elevated: {
      backgroundColor: colors.backgroundSecondary,
      borderRadius: borderRadius.xl,
      padding: spacing.xl,
      ...shadows.lg,
    },
  },
  
  // Text styles
  text: {
    heading1: {
      fontSize: typography.fontSize['4xl'],
      fontWeight: typography.fontWeight.bold,
      color: colors.text,
      lineHeight: typography.lineHeight.tight * typography.fontSize['4xl'],
    },
    heading2: {
      fontSize: typography.fontSize['3xl'],
      fontWeight: typography.fontWeight.bold,
      color: colors.text,
      lineHeight: typography.lineHeight.tight * typography.fontSize['3xl'],
    },
    heading3: {
      fontSize: typography.fontSize['2xl'],
      fontWeight: typography.fontWeight.semibold,
      color: colors.text,
      lineHeight: typography.lineHeight.normal * typography.fontSize['2xl'],
    },
    heading4: {
      fontSize: typography.fontSize.xl,
      fontWeight: typography.fontWeight.semibold,
      color: colors.text,
      lineHeight: typography.lineHeight.normal * typography.fontSize.xl,
    },
    body: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.normal,
      color: colors.text,
      lineHeight: typography.lineHeight.normal * typography.fontSize.base,
    },
    bodyLarge: {
      fontSize: typography.fontSize.lg,
      fontWeight: typography.fontWeight.normal,
      color: colors.text,
      lineHeight: typography.lineHeight.normal * typography.fontSize.lg,
    },
    caption: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.normal,
      color: colors.textSecondary,
      lineHeight: typography.lineHeight.normal * typography.fontSize.sm,
    },
    small: {
      fontSize: typography.fontSize.xs,
      fontWeight: typography.fontWeight.normal,
      color: colors.textLight,
      lineHeight: typography.lineHeight.normal * typography.fontSize.xs,
    },
  },
};

// Layout
export const layout = {
  // Container styles
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  
  // Screen padding
  screenPadding: {
    paddingHorizontal: spacing.xl,
  },
  
  // Section spacing
  section: {
    marginBottom: spacing['3xl'],
  },
  
  // Row styles
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  
  // Column styles
  column: {
    flexDirection: 'column',
  },
  
  // Center content
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Space between
  spaceBetween: {
    justifyContent: 'space-between',
  },
  
  // Space around
  spaceAround: {
    justifyContent: 'space-around',
  },
};

// Animation timings
export const animations = {
  fast: 150,
  normal: 250,
  slow: 350,
  slower: 500,
};

// Breakpoints (for responsive design)
export const breakpoints = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
};

// Export default theme object
const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  components,
  layout,
  animations,
  breakpoints,
};

export default theme; 