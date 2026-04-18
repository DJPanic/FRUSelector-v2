import React from 'react';
import './FamilySelector.css';
import { SurfaceFamily } from '../shared/types';

interface FamilySelectorProps {
  families: SurfaceFamily[];
  selectedFamilyId: string | null;
  onSelectFamily: (familyId: string) => void;
}

export const FamilySelector: React.FC<FamilySelectorProps> = ({
  families,
  selectedFamilyId,
  onSelectFamily,
}) => {
  return (
    <div className="family-selector">
      <h2>Step 1: Select Device Family</h2>
      <div className="family-buttons">
        {families.map((family) => (
          <button
            key={family.id}
            className={`family-btn ${selectedFamilyId === family.id ? 'active' : ''}`}
            onClick={() => onSelectFamily(family.id)}
          >
            {family.name}
          </button>
        ))}
      </div>
    </div>
  );
};
