import { SurfaceFamily, SKUReference, FRU } from './types';

// Hardcoded Surface data - In production, this would be fetched from external sources
export const SURFACE_DATA: SurfaceFamily[] = [
  {
    id: 'laptop',
    name: 'Surface Laptop',
    models: [
      {
        id: 'laptop7',
        name: 'Surface Laptop 7',
        skuBaseNumber: '1P1',
        variants: [
          {
            id: 'processor',
            name: 'Processor',
            values: [
              { id: 'snapdragon-x-plus', label: 'Snapdragon X Plus' },
              { id: 'snapdragon-x', label: 'Snapdragon X' },
            ],
          },
          {
            id: 'ram',
            name: 'RAM',
            values: [
              { id: '16gb', label: '16 GB' },
              { id: '32gb', label: '32 GB' },
            ],
          },
          {
            id: 'storage',
            name: 'Storage',
            values: [
              { id: '256gb', label: '256 GB SSD' },
              { id: '512gb', label: '512 GB SSD' },
              { id: '1tb', label: '1 TB SSD' },
            ],
          },
          {
            id: 'screen',
            name: 'Screen',
            values: [
              { id: 'touchscreen', label: 'Touchscreen' },
              { id: 'standard', label: 'Standard Display' },
            ],
          },
        ],
        serviceGuideUrl: 'https://www.microsoft.com/en-us/download/details.aspx?id=100440',
      },
      {
        id: 'laptop6',
        name: 'Surface Laptop 6',
        skuBaseNumber: '1P0',
        variants: [
          {
            id: 'processor',
            name: 'Processor',
            values: [
              { id: 'ultra', label: 'Intel Core Ultra' },
            ],
          },
          {
            id: 'ram',
            name: 'RAM',
            values: [
              { id: '16gb', label: '16 GB' },
              { id: '32gb', label: '32 GB' },
              { id: '64gb', label: '64 GB' },
            ],
          },
          {
            id: 'storage',
            name: 'Storage',
            values: [
              { id: '512gb', label: '512 GB SSD' },
              { id: '1tb', label: '1 TB SSD' },
              { id: '2tb', label: '2 TB SSD' },
            ],
          },
          {
            id: 'screen',
            name: 'Screen',
            values: [
              { id: 'touchscreen', label: 'Touchscreen' },
              { id: 'standard', label: 'Standard Display' },
            ],
          },
        ],
        serviceGuideUrl: 'https://www.microsoft.com/en-us/download/details.aspx?id=100440',
      },
    ],
  },
  {
    id: 'book',
    name: 'Surface Book',
    models: [
      {
        id: 'book3',
        name: 'Surface Book 3',
        skuBaseNumber: '2B0',
        variants: [
          {
            id: 'processor',
            name: 'Processor',
            values: [
              { id: '10th-i5', label: '10th Gen Intel i5' },
              { id: '10th-i7', label: '10th Gen Intel i7' },
            ],
          },
          {
            id: 'ram',
            name: 'RAM',
            values: [
              { id: '8gb', label: '8 GB' },
              { id: '16gb', label: '16 GB' },
              { id: '32gb', label: '32 GB' },
            ],
          },
          {
            id: 'storage',
            name: 'Storage',
            values: [
              { id: '256gb', label: '256 GB SSD' },
              { id: '512gb', label: '512 GB SSD' },
              { id: '1tb', label: '1 TB SSD' },
            ],
          },
          {
            id: 'gpu',
            name: 'Graphics',
            values: [
              { id: 'integrated', label: 'Integrated Graphics' },
              { id: 'gtx1650', label: 'NVIDIA GTX 1650' },
            ],
          },
          {
            id: 'screen',
            name: 'Screen Size',
            values: [
              { id: '13.5in', label: '13.5 inch' },
              { id: '15in', label: '15 inch' },
            ],
          },
        ],
        serviceGuideUrl: 'https://www.microsoft.com/en-us/download/details.aspx?id=100440',
      },
    ],
  },
  {
    id: 'pro',
    name: 'Surface Pro',
    models: [
      {
        id: 'pro10',
        name: 'Surface Pro 10',
        skuBaseNumber: '2PE',
        variants: [
          {
            id: 'processor',
            name: 'Processor',
            values: [
              { id: 'ultra5', label: 'Intel Core Ultra 5' },
              { id: 'ultra7', label: 'Intel Core Ultra 7' },
            ],
          },
          {
            id: 'ram',
            name: 'RAM',
            values: [
              { id: '16gb', label: '16 GB' },
              { id: '32gb', label: '32 GB' },
            ],
          },
          {
            id: 'storage',
            name: 'Storage',
            values: [
              { id: '256gb', label: '256 GB SSD' },
              { id: '512gb', label: '512 GB SSD' },
              { id: '1tb', label: '1 TB SSD' },
            ],
          },
          {
            id: 'keyboard',
            name: 'Keyboard Type',
            values: [
              { id: 'standard', label: 'Standard' },
              { id: 'signature', label: 'Signature' },
            ],
          },
        ],
        serviceGuideUrl: 'https://www.microsoft.com/en-us/download/details.aspx?id=100440',
      },
      {
        id: 'pro9',
        name: 'Surface Pro 9',
        skuBaseNumber: '2PD',
        variants: [
          {
            id: 'processor',
            name: 'Processor',
            values: [
              { id: '12th-i5', label: '12th Gen Intel i5' },
              { id: '12th-i7', label: '12th Gen Intel i7' },
            ],
          },
          {
            id: 'ram',
            name: 'RAM',
            values: [
              { id: '8gb', label: '8 GB' },
              { id: '16gb', label: '16 GB' },
              { id: '32gb', label: '32 GB' },
            ],
          },
          {
            id: 'storage',
            name: 'Storage',
            values: [
              { id: '128gb', label: '128 GB SSD' },
              { id: '256gb', label: '256 GB SSD' },
              { id: '512gb', label: '512 GB SSD' },
              { id: '1tb', label: '1 TB SSD' },
            ],
          },
        ],
        serviceGuideUrl: 'https://www.microsoft.com/en-us/download/details.aspx?id=100440',
      },
    ],
  },
];

// Sample FRU data - In production, this would be parsed from service guides
export const FRU_DATA: FRU[] = [
  {
    partNumber: '5V6-00001',
    description: 'Battery',
    category: 'Power',
    applicableSkus: ['1P1-16-256'],
  },
  {
    partNumber: '5V6-00002',
    description: 'Charging Port',
    category: 'Power',
    applicableSkus: ['1P1-16-256', '1P1-16-512', '1P0-16-512'],
  },
  {
    partNumber: '5V6-00003',
    description: 'SSD Module (256GB)',
    category: 'Storage',
    applicableSkus: ['1P1-16-256'],
  },
  {
    partNumber: '5V6-00004',
    description: 'Fan Assembly',
    category: 'Cooling',
    applicableSkus: ['2B0-i7-16-512', '2B0-i7-16-512-gtx'],
  },
  {
    partNumber: '5V6-00005',
    description: 'Keyboard',
    category: 'Input',
    applicableSkus: ['2PE-ultra5-16-256'],
  },
  {
    partNumber: '5V6-00006',
    description: 'Display Panel',
    category: 'Display',
    applicableSkus: ['1P1-16-256', '1P1-32-512', '2PD-i5-16-256'],
  },
];

// Sample SKU data - In production, this would be scraped from Microsoft Learn
export const SKU_DATA: SKUReference[] = [
  {
    sku: '1P1-16-256',
    description: 'Surface Laptop 7 - Snapdragon X - 16GB RAM - 256GB SSD - Standard',
    family: 'Surface Laptop',
    model: 'Surface Laptop 7',
    configuration: {
      processor: 'Snapdragon X',
      ram: '16GB',
      storage: '256GB',
      screen: 'Standard',
    },
  },
  {
    sku: '1P1-16-512',
    description: 'Surface Laptop 7 - Snapdragon X - 16GB RAM - 512GB SSD - Touchscreen',
    family: 'Surface Laptop',
    model: 'Surface Laptop 7',
    configuration: {
      processor: 'Snapdragon X',
      ram: '16GB',
      storage: '512GB',
      screen: 'Touchscreen',
    },
  },
  {
    sku: '1P0-16-512',
    description: 'Surface Laptop 6 - Intel Core Ultra - 16GB RAM - 512GB SSD - Touchscreen',
    family: 'Surface Laptop',
    model: 'Surface Laptop 6',
    configuration: {
      processor: 'Intel Core Ultra',
      ram: '16GB',
      storage: '512GB',
      screen: 'Touchscreen',
    },
  },
  {
    sku: '2B0-i7-16-512',
    description: 'Surface Book 3 - Intel i7 - 16GB RAM - 512GB SSD - 13.5in',
    family: 'Surface Book',
    model: 'Surface Book 3',
    configuration: {
      processor: '10th Gen Intel i7',
      ram: '16GB',
      storage: '512GB',
      gpu: 'Integrated Graphics',
      screen: '13.5in',
    },
  },
  {
    sku: '2B0-i7-16-512-gtx',
    description: 'Surface Book 3 - Intel i7 - 16GB RAM - 512GB SSD - 13.5in - GTX 1650',
    family: 'Surface Book',
    model: 'Surface Book 3',
    configuration: {
      processor: '10th Gen Intel i7',
      ram: '16GB',
      storage: '512GB',
      gpu: 'NVIDIA GTX 1650',
      screen: '13.5in',
    },
  },
  {
    sku: '2PE-ultra5-16-256',
    description: 'Surface Pro 10 - Intel Core Ultra 5 - 16GB RAM - 256GB SSD',
    family: 'Surface Pro',
    model: 'Surface Pro 10',
    configuration: {
      processor: 'Intel Core Ultra 5',
      ram: '16GB',
      storage: '256GB',
      keyboard: 'Standard',
    },
  },
  {
    sku: '2PD-i5-16-256',
    description: 'Surface Pro 9 - Intel i5 - 16GB RAM - 256GB SSD',
    family: 'Surface Pro',
    model: 'Surface Pro 9',
    configuration: {
      processor: '12th Gen Intel i5',
      ram: '16GB',
      storage: '256GB',
    },
  },
];
