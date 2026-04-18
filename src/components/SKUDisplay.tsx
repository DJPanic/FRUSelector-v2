import React from 'react';
import './SKUDisplay.css';
import { SKUReference, FRU } from '../shared/types';

interface SKUDisplayProps {
  sku: SKUReference | null;
  frus: FRU[];
  configuration: { [key: string]: string };
}

export const SKUDisplay: React.FC<SKUDisplayProps> = ({ sku, frus, configuration }) => {
  if (!sku) {
    return (
      <div className="sku-display empty">
        <p>Complete the configuration above to see matching SKU and FRU parts.</p>
      </div>
    );
  }

  return (
    <div className="sku-display">
      <div className="sku-section">
        <h3>Matched SKU</h3>
        <div className="sku-info">
          <div className="sku-number">
            <strong>SKU:</strong> <code>{sku.sku}</code>
          </div>
          <div className="sku-description">
            <strong>Description:</strong> {sku.description}
          </div>
          <div className="sku-config">
            <strong>Configuration:</strong>
            <ul>
              {Object.entries(sku.configuration)
                .filter(([, value]) => value)
                .map(([key, value]) => (
                  <li key={key}>
                    {key.charAt(0).toUpperCase() + key.slice(1)}: {value}
                  </li>
                ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="fru-section">
        <h3>Applicable FRU Parts</h3>
        {frus.length > 0 ? (
          <div className="fru-list">
            {frus.map((fru) => (
              <div key={fru.partNumber} className="fru-item">
                <div className="fru-number">
                  <strong>Part #:</strong> {fru.partNumber}
                </div>
                <div className="fru-description">{fru.description}</div>
                <div className="fru-category">
                  <span className="category-badge">{fru.category}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-frus">No FRU parts found for this configuration.</p>
        )}
      </div>
    </div>
  );
};
