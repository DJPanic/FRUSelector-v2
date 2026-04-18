# Surface FRU Selector

A standalone desktop application built with Electron and React that helps partners and customers find the right FRU (Field Replaceable Unit) parts to order when repairing Surface devices.

## Features

- **Device Family Selection**: Browse Surface Laptop, Surface Book, Surface Pro, and more
- **Model Selection**: Choose from available Surface device models
- **Configuration Builder**: Select processor, RAM, storage, keyboard, screen type, and other variants
- **Automatic SKU Matching**: Instantly matches your configuration to the correct Surface SKU
- **FRU Parts Lookup**: Displays all applicable replacement parts for your specific device configuration
- **Offline-capable**: Can work with cached data for field technicians

## Tech Stack

- **Electron**: Desktop application framework
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Node.js**: Runtime

## Getting Started

### Prerequisites

- Node.js 16+ and npm 7+
- Git

### Installation

1. Clone the repository or navigate to the project folder:
   ```bash
   cd fru-selector
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Start the development server with hot-reload:

```bash
npm run dev
```

This will start both the React development server and Electron in watch mode.

### Building

Build for production:

```bash
npm run build
```

This creates optimized production builds and packages the application.

### Testing

Run the test suite:

```bash
npm test
```

## Project Structure

```
fru-selector/
├── public/
│   └── index.html
├── src/
│   ├── main/
│   │   ├── index.ts          # Electron main process
│   │   └── preload.ts        # Preload script for IPC
│   ├── renderer/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── App.tsx           # Main app component
│   │   ├── index.tsx         # React entry point
│   │   └── index.css         # Global styles
│   └── shared/
│       ├── types.ts          # TypeScript type definitions
│       └── data.ts           # Sample data and utilities
├── package.json
├── tsconfig.json
└── README.md
```

## Usage

1. **Select Device Family**: Click on a Surface device family (Laptop, Book, Pro, etc.)
2. **Choose Model**: Select the specific Surface model
3. **Configure Variants**: Use dropdowns to select processor, RAM, storage, and other options
4. **View Results**: The application automatically displays:
   - The matched SKU (Stock Keeping Unit)
   - A complete list of applicable FRU parts
   - Part numbers and descriptions for ordering

## Data Sources

- **SKU Reference**: Based on Microsoft's [Surface System SKU Reference](https://learn.microsoft.com/en-us/surface/surface-system-sku-reference)
- **Service Guides**: Integrated with Microsoft's [Surface Service Guides](https://www.microsoft.com/en-us/download/details.aspx?id=100440)

## Contributing

To add or update device data:

1. Update the device configurations in `src/shared/data.ts`
2. Add corresponding SKU references and FRU mappings
3. Test with the dev server to verify matching works correctly

## License

MIT

## Support

For issues or questions about Surface device parts, consult:
- [Microsoft Surface Support](https://support.microsoft.com/en-us/surface)
- [Surface Devices Tech Specs](https://www.microsoft.com/en-us/surface/business/device-comparison)

---

**Note**: This application is designed for authorized repair partners and customers. Always verify part compatibility with official Microsoft documentation before ordering replacement parts.
