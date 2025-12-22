# Quick Integration Example

This example shows exactly how to add the translate button to your Docusaurus navbar in 3 simple steps.

## Step 1: Wrap Your App

Create `src/theme/Root.js`:

```javascript
import React from 'react';
import { PageTranslationWrapper } from './src/pageTranslation';

// This wraps your entire Docusaurus site
export default function Root({ children }) {
  return (
    <PageTranslationWrapper>
      {children}
    </PageTranslationWrapper>
  );
}
```

## Step 2: Add Button to Navbar

Create `src/theme/NavbarItem/ComponentTypes.js`:

```javascript
import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import { NavbarTranslateButton } from '../../pageTranslation';

export default {
  ...ComponentTypes,
  'custom-translateButton': NavbarTranslateButton,
};
```

## Step 3: Configure in docusaurus.config.js

```javascript
module.exports = {
  // ... other config
  themeConfig: {
    navbar: {
      items: [
        // ... other navbar items
        {
          type: 'custom-translateButton',
          position: 'right',
          variant: 'minimal',
          showLabel: true,
        },
      ],
    },
  },
};
```

## That's it!

Your Docusaurus site now has a working translate button in the navbar.

## Alternative: Direct Swizzle Method

If you prefer to swizzle the navbar directly:

```bash
npm run swizzle @docusaurus/theme-classic Navbar -- --eject
```

Then edit `src/theme/Navbar/index.js` and add:

```javascript
import { NavbarTranslateButton } from '../pageTranslation';

// Inside your navbar JSX, add:
<NavbarTranslateButton variant="minimal" />
```

## Customization Examples

### Icon Only (Mobile-Friendly)

```javascript
{
  type: 'custom-translateButton',
  position: 'right',
  variant: 'minimal',
  showLabel: false,
}
```

### With Urdu Label

```javascript
{
  type: 'custom-translateButton',
  position: 'right',
  label: 'اردو میں ترجمہ کریں',
  activeLabel: 'اصل متن',
  variant: 'default',
}
```

### Outline Style

```javascript
{
  type: 'custom-translateButton',
  position: 'right',
  variant: 'outline',
}
```

## Testing

1. Start your Docusaurus site: `npm start`
2. Click the translate button in navbar
3. Watch the page content translate to Urdu
4. Click again to restore original
5. Navigate to another page - translation persists!

## Troubleshooting

**Button doesn't appear:**
- Clear `.docusaurus` cache: `rm -rf .docusaurus`
- Restart dev server

**Translation doesn't work:**
- Check browser console for errors
- Verify backend is running at `http://localhost:8000`
- Test `/api/health` endpoint

**Styles look weird:**
- Import styles in `src/css/custom.css`:
  ```css
  @import url('../components/NavbarTranslateButton/styles.css');
  ```
