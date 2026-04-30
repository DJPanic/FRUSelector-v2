export interface SurfaceVariant {
  id: string;
  name: string;
  values: VariantOption[];
}

export interface VariantOption {
  id: string;
  label: string;
}

export interface SurfaceModel {
  id: string;
  name: string;
  skuBaseNumber: string;
  variants: SurfaceVariant[];
  serviceGuideUrl?: string;
}

export interface SurfaceFamily {
  id: string;
  name: string;
  models: SurfaceModel[];
}

export interface SKUReference {
  sku: string;
  description: string;
  family: string;
  model: string;
  configuration: {
    processor?: string;
    ram?: string;
    storage?: string;
    keyboard?: string;
    screen?: string;
    gpu?: string;
    [key: string]: string | undefined;
  };
}

export interface FRU {
  partNumber: string;
  description: string;
  category: string;
  applicableSkus: string[];
}

export interface ScrapedPart {
  part_number: string;
  description: string;
  category: string;
  substitute?: string;
}

export interface ScrapedDevice {
  name: string;
  parts: ScrapedPart[];
}

export interface ScrapedData {
  generatedAt: string;
  source: string;
  deviceCount: number;
  partCount: number;
  devices: ScrapedDevice[];
}

export interface DeviceConfiguration {
  familyId: string;
  modelId: string;
  variantSelections: {
    [variantId: string]: string;
  };
}
