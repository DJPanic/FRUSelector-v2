import React from 'react';
import './ModelSelector.css';
import { SurfaceModel } from '../shared/types';

interface ModelSelectorProps {
  models: SurfaceModel[];
  selectedModelId: string | null;
  onSelectModel: (modelId: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModelId,
  onSelectModel,
}) => {
  return (
    <div className="model-selector">
      <h2>Step 2: Select Model</h2>
      <div className="model-list">
        {models.map((model) => (
          <div
            key={model.id}
            className={`model-item ${selectedModelId === model.id ? 'active' : ''}`}
            onClick={() => onSelectModel(model.id)}
          >
            <div className="model-name">{model.name}</div>
            <div className="model-sku">SKU Base: {model.skuBaseNumber}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
