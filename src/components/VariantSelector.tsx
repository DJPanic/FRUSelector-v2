import React from 'react';
import './VariantSelector.css';
import { SurfaceVariant } from '../shared/types';

interface VariantSelectorProps {
  variants: SurfaceVariant[];
  selections: { [key: string]: string };
  onVariantChange: (variantId: string, optionId: string) => void;
}

export const VariantSelector: React.FC<VariantSelectorProps> = ({
  variants,
  selections,
  onVariantChange,
}) => {
  return (
    <div className="variant-selector">
      <h2>Step 3: Configure Variants</h2>
      <div className="variants-grid">
        {variants.map((variant) => (
          <div key={variant.id} className="variant-group">
            <label htmlFor={variant.id}>{variant.name}</label>
            <select
              id={variant.id}
              value={selections[variant.id] || ''}
              onChange={(e) => onVariantChange(variant.id, e.target.value)}
              className="variant-dropdown"
            >
              <option value="">Select {variant.name}...</option>
              {variant.values.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
};
