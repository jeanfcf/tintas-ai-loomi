import React, { useState } from 'react';
import styled from 'styled-components';
import { Search, Star } from 'lucide-react';
import apiClient, { API_ENDPOINTS } from '../config/api';

const SearchContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const SearchHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const Title = styled.h2`
  color: #1f2937;
  margin: 0 0 0.5rem 0;
  font-size: 1.875rem;
  font-weight: bold;
`;

const Subtitle = styled.p`
  color: #6b7280;
  margin: 0;
  font-size: 1rem;
`;

const SearchForm = styled.form`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 1rem;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const SearchButton = styled.button`
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const FiltersContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const FilterSelect = styled.select`
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  outline: none;
  font-size: 0.9rem;

  &:focus {
    border-color: #3b82f6;
  }
`;

const ResultsContainer = styled.div`
  display: grid;
  gap: 1rem;
`;

const PaintCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
`;

const PaintHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 1rem;
`;

const PaintName = styled.h3`
  color: #1f2937;
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
`;

const PaintColor = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.9rem;
`;

const ColorSwatch = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: ${props => props.color || '#e5e7eb'};
  border: 1px solid #d1d5db;
`;

const PaintDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
`;

const DetailItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
`;

const DetailLabel = styled.span`
  color: #6b7280;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const DetailValue = styled.span`
  color: #1f2937;
  font-size: 0.9rem;
`;

const FeaturesContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const FeatureTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const PriceContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
`;

const Price = styled.span`
  color: #059669;
  font-size: 1.125rem;
  font-weight: 600;
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #fbbf24;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #6b7280;
  padding: 2rem;
  font-style: italic;
`;

const ErrorMessage = styled.div`
  text-align: center;
  color: #dc2626;
  padding: 2rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
`;

function PaintSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    environment: '',
    finish_type: '',
    line: ''
  });
  const [paints, setPaints] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (filters.color) params.append('color', filters.color);
      if (filters.environment) params.append('environment', filters.environment);
      if (filters.finish_type) params.append('finish_type', filters.finish_type);
      if (filters.line) params.append('line', filters.line);
      if (filters.surface_types) params.append('surface_types', filters.surface_types);
      if (filters.features) params.append('features', filters.features);

      const response = await apiClient.get(`${API_ENDPOINTS.PAINTS.LIST_PUBLIC}?${params}`);
      setPaints(response.data.items || []);
    } catch (err) {
      setError('Erro ao buscar tintas. Tente novamente.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getFeatures = (paint) => {
    const features = [];
    if (paint.is_washable) features.push('Lavável');
    if (paint.is_anti_mold) features.push('Anti-mofo');
    if (paint.is_odorless) features.push('Sem odor');
    if (paint.is_heat_resistant) features.push('Resistente ao calor');
    if (paint.is_weather_resistant) features.push('Resistente ao clima');
    return features;
  };

  const getSurfaceTypes = (paint) => {
    return paint.surface_types || [];
  };

  const getColorCode = (paint) => {
    // Usar o color_hex da API se disponível, senão usar mapeamento local
    if (paint.color_hex) {
      return paint.color_hex;
    }
    
    const colorMap = {
      'azul': '#3b82f6',
      'vermelho': '#dc2626',
      'verde': '#059669',
      'amarelo': '#d97706',
      'branco': '#f9fafb',
      'preto': '#1f2937',
      'cinza': '#6b7280',
      'rosa': '#ec4899',
      'roxo': '#7c3aed',
      'laranja': '#ea580c'
    };
    return colorMap[paint.color.toLowerCase()] || '#e5e7eb';
  };

  return (
    <SearchContainer>
      <SearchHeader>
        <Title>Buscar Tintas Suvinil</Title>
        <Subtitle>Encontre a tinta perfeita para seu projeto</Subtitle>
      </SearchHeader>

      <SearchForm onSubmit={handleSearch}>
        <SearchInput
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Digite o que você está procurando..."
        />
        <SearchButton type="submit" disabled={isLoading}>
          <Search size={16} />
          Buscar
        </SearchButton>
      </SearchForm>

      <FiltersContainer>
        <FilterSelect
          value={filters.environment}
          onChange={(e) => setFilters(prev => ({ ...prev, environment: e.target.value }))}
        >
          <option value="">Todos os ambientes</option>
          <option value="interno">Interno</option>
          <option value="externo">Externo</option>
        </FilterSelect>

        <FilterSelect
          value={filters.finish_type}
          onChange={(e) => setFilters(prev => ({ ...prev, finish_type: e.target.value }))}
        >
          <option value="">Todos os acabamentos</option>
          <option value="fosco">Fosco</option>
          <option value="acetinado">Acetinado</option>
          <option value="brilhante">Brilhante</option>
          <option value="semi_brilho">Semi-brilho</option>
        </FilterSelect>

        <FilterSelect
          value={filters.line}
          onChange={(e) => setFilters(prev => ({ ...prev, line: e.target.value }))}
        >
          <option value="">Todas as linhas</option>
          <option value="premium">Premium</option>
          <option value="standard">Standard</option>
          <option value="economy">Economy</option>
        </FilterSelect>

      </FiltersContainer>

      <ResultsContainer>
        {isLoading && (
          <LoadingMessage>
            <Search size={20} />
            Buscando tintas...
          </LoadingMessage>
        )}

        {error && (
          <ErrorMessage>
            {error}
          </ErrorMessage>
        )}

        {!isLoading && !error && paints.length === 0 && (
          <LoadingMessage>
            Nenhuma tinta encontrada. Tente ajustar os filtros.
          </LoadingMessage>
        )}

        {!isLoading && !error && paints.map(paint => (
          <PaintCard key={paint.id}>
            <PaintHeader>
              <div>
                <PaintName>{paint.name}</PaintName>
                <PaintColor>
                  <ColorSwatch color={getColorCode(paint)} />
                  {paint.color}
                  {paint.color_hex && (
                    <span style={{ marginLeft: '0.5rem', fontSize: '0.8rem', color: '#6b7280' }}>
                      ({paint.color_hex})
                    </span>
                  )}
                </PaintColor>
              </div>
            </PaintHeader>

            <PaintDetails>
              <DetailItem>
                <DetailLabel>Ambiente</DetailLabel>
                <DetailValue>{paint.environment}</DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>Acabamento</DetailLabel>
                <DetailValue>{paint.finish_type}</DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>Linha</DetailLabel>
                <DetailValue>{paint.line}</DetailValue>
              </DetailItem>
              <DetailItem>
                <DetailLabel>Superfície</DetailLabel>
                <DetailValue>
                  {getSurfaceTypes(paint).length > 0 ? (
                    <FeaturesContainer>
                      {getSurfaceTypes(paint).map(surfaceType => (
                        <FeatureTag key={surfaceType}>{surfaceType}</FeatureTag>
                      ))}
                    </FeaturesContainer>
                  ) : (
                    'N/A'
                  )}
                </DetailValue>
              </DetailItem>
            </PaintDetails>

            <FeaturesContainer>
              {getFeatures(paint).map(feature => (
                <FeatureTag key={feature}>{feature}</FeatureTag>
              ))}
            </FeaturesContainer>

            <PriceContainer>
              <Price>
                {paint.price_per_liter ? `R$ ${paint.price_per_liter.toFixed(2)}/L` : 'Preço sob consulta'}
              </Price>
              <Rating>
                <Star size={16} fill="currentColor" />
                <span>4.5</span>
              </Rating>
            </PriceContainer>
          </PaintCard>
        ))}
      </ResultsContainer>
    </SearchContainer>
  );
}

export default PaintSearch;
