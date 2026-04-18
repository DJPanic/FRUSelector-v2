import React, { useState, useMemo } from 'react';
import './App.css';
import { FamilySelector } from './components/FamilySelector';
import { ModelSelector } from './components/ModelSelector';
import { VariantSelector } from './components/VariantSelector';
import { SKUDisplay } from './components/SKUDisplay';
import { SURFACE_DATA, SKU_DATA, FRU_DATA } from './shared/data';
import { SurfaceFamily, SurfaceModel, SKUReference, FRU } from './shared/types';

// Normalize strings for comparison: lowercase, strip spaces and common suffixes
const normalize = (s: string): string =>
  s.toLowerCase().replace(/\s+/g, '').replace(/ssd$/, '');

const App = () => {
  const [selectedFamilyId, setSelectedFamilyId] = useState<string | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
  const [variantSelections, setVariantSelections] = useState<{ [key: string]: string }>({});

  // Get the selected family
  const selectedFamily = useMemo(
    () => SURFACE_DATA.find((f) => f.id === selectedFamilyId),
    [selectedFamilyId]
  );

  // Get the available models for the selected family
  const availableModels = useMemo(
    () => (selectedFamily ? selectedFamily.models : []),
    [selectedFamily]
  );

  // Get the selected model
  const selectedModel = useMemo(
    () => availableModels.find((m) => m.id === selectedModelId),
    [availableModels, selectedModelId]
  );

  // Get the variants for the selected model
  const modelVariants = useMemo(
    () => (selectedModel ? selectedModel.variants : []),
    [selectedModel]
  );

  // Reset model selection when family changes
  const handleFamilySelect = (familyId: string) => {
    setSelectedFamilyId(familyId);
    setSelectedModelId(null);
    setVariantSelections({});
  };

  // Reset variants when model changes
  const handleModelSelect = (modelId: string) => {
    setSelectedModelId(modelId);
    setVariantSelections({});
  };

  // Handle variant selection
  const handleVariantChange = (variantId: string, optionId: string) => {
    setVariantSelections((prev) => ({
      ...prev,
      [variantId]: optionId,
    }));
  };

  // Match SKU based on current selection
  const matchedSku = useMemo(() => {
    if (!selectedModel || !variantSelections) return null;

    // Find all variants that have been selected
    const allVariantsSelected = modelVariants.every((v) => variantSelections[v.id]);

    if (!allVariantsSelected) return null;

    // Build a search criteria based on variant selections
    const skuCandidates = SKU_DATA.filter((sku) => {
      // Check if SKU matches the family, model, and all variant selections
      if (
        sku.family.toLowerCase() !== selectedFamily?.name.toLowerCase() ||
        !sku.model.includes(selectedModel.name)
      ) {
        return false;
      }

      // Check all variant selections
      for (const [variantId, selectedOptionId] of Object.entries(variantSelections)) {
        const variant = modelVariants.find((v) => v.id === variantId);
        if (!variant) continue;

        const selectedOption = variant.values.find((v) => v.id === selectedOptionId);
        if (!selectedOption) continue;

        // Match using variant id (e.g., "gpu", "screen") which aligns with SKU config keys
        const variantKey = variant.id.toLowerCase();
        const optionNorm = normalize(selectedOption.label);

        // Try to match the variant category in the SKU config
        const skuConfigKey = Object.keys(sku.configuration).find(
          (key) => key.toLowerCase() === variantKey
        );

        if (skuConfigKey) {
          const skuNorm = normalize(sku.configuration[skuConfigKey] || '');
          if (!skuNorm.includes(optionNorm) && !optionNorm.includes(skuNorm)) {
            return false;
          }
        }
      }

      return true;
    });

    return skuCandidates.length > 0 ? skuCandidates[0] : null;
  }, [selectedModel, selectedFamily, variantSelections, modelVariants]);

  // Get FRUs for the matched SKU
  const applicableFrus = useMemo(() => {
    if (!matchedSku) return [];
    return FRU_DATA.filter((fru) => fru.applicableSkus.includes(matchedSku.sku));
  }, [matchedSku]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Surface Device Part Finder</h1>
        <p>Find the right FRU parts for your Surface device repair</p>
      </header>

      <div className="app-container">
        <div className="app-content">
          <FamilySelector
            families={SURFACE_DATA}
            selectedFamilyId={selectedFamilyId}
            onSelectFamily={handleFamilySelect}
          />

          {selectedFamily && (
            <ModelSelector
              models={availableModels}
              selectedModelId={selectedModelId}
              onSelectModel={handleModelSelect}
            />
          )}

          {selectedModel && (
            <VariantSelector
              variants={modelVariants}
              selections={variantSelections}
              onVariantChange={handleVariantChange}
            />
          )}
        </div>

        <SKUDisplay sku={matchedSku} frus={applicableFrus} configuration={variantSelections} />
      </div>
    </div>
  );
};

export default App;
