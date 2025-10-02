import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { Plus, Edit, Trash2, X, Upload, Download, FileText } from 'lucide-react';
import apiClient, { API_ENDPOINTS } from '../config/api';
import { useAuth } from '../contexts/AuthContext';

const ManagementContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const Title = styled.h2`
  color: #1f2937;
  margin: 0;
  font-size: 1.875rem;
  font-weight: bold;
`;

const AddButton = styled.button`
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;

  &:hover {
    background: #059669;
  }
`;

const ImportButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const DownloadButton = styled.button`
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;

  &:hover {
    background: #4b5563;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const ImportModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ImportModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
`;

const ImportModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const ImportModalTitle = styled.h3`
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: bold;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  color: #6b7280;
  
  &:hover {
    background: #f3f4f6;
  }
`;

const FileInput = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  cursor: pointer;
  margin-bottom: 1rem;
  
  &:hover {
    border-color: #3b82f6;
    background: #eff6ff;
  }
`;

const ImportOptions = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const OptionGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Checkbox = styled.input`
  width: 1rem;
  height: 1rem;
`;

const Label = styled.label`
  color: #374151;
  font-weight: 500;
  cursor: pointer;
`;

const ImportActions = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
`;

const CancelButton = styled.button`
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background: #4b5563;
  }
`;

const ImportSubmitButton = styled.button`
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: #059669;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ImportResult = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: ${props => props.success ? '#d1fae5' : '#fee2e2'};
  border: 1px solid ${props => props.success ? '#a7f3d0' : '#fecaca'};
`;

const ImportResultTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: ${props => props.success ? '#065f46' : '#991b1b'};
  font-size: 1rem;
  font-weight: bold;
`;

const ImportResultText = styled.p`
  margin: 0;
  color: ${props => props.success ? '#047857' : '#dc2626'};
  font-size: 0.875rem;
`;

const ErrorList = styled.ul`
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
  color: #dc2626;
  font-size: 0.875rem;
`;

const CSVFormatInfo = styled.div`
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
`;

const CSVFormatTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 0.875rem;
  font-weight: bold;
`;

const CSVFormatText = styled.p`
  margin: 0;
  color: #6b7280;
  font-size: 0.75rem;
  line-height: 1.4;
`;

const SearchContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const SearchInput = styled.input`
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  @media (max-width: 768px) {
    min-width: 100%;
  }
`;

const FilterSelect = styled.select`
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
  background: white;
  min-width: 150px;

  &:focus {
    border-color: #3b82f6;
  }
  
  @media (max-width: 768px) {
    min-width: 100%;
  }
`;

const MultiSelectContainer = styled.div`
  position: relative;
  min-width: 200px;
  
  @media (max-width: 768px) {
    min-width: 100%;
  }
`;

const MultiSelectButton = styled.button`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
  }
`;

const MultiSelectDropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
`;

const MultiSelectOption = styled.label`
  display: flex;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  
  &:hover {
    background: #f3f4f6;
  }
  
  input {
    margin-right: 0.5rem;
  }
`;

const SelectedTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.25rem;
`;

const SelectedTag = styled.span`
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const RemoveTagButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0;
  margin-left: 0.25rem;
  
  &:hover {
    color: #fbbf24;
  }
`;

const PaintsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
`;

const PaginationInfo = styled.span`
  color: #6b7280;
  font-size: 0.9rem;
`;

const PaginationButtons = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const PaginationButton = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: #f3f4f6;
    border-color: #9ca3af;
  }

  &:disabled {
    background: #f9fafb;
    color: #9ca3af;
    cursor: not-allowed;
  }
`;

const PaintCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const PaintHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
`;

const PaintName = styled.h3`
  color: #1f2937;
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
`;

const PaintActions = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ActionButton = styled.button`
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;

  &.edit {
    background: #f3f4f6;
    color: #374151;

    &:hover {
      background: #e5e7eb;
    }
  }

  &.delete {
    background: #fef2f2;
    color: #dc2626;

    &:hover {
      background: #fecaca;
    }
  }
`;

const PaintInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const InfoLabel = styled.span`
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
`;

const InfoValue = styled.span`
  color: #1f2937;
  font-size: 0.9rem;
`;

const FeaturesList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const FeaturesContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const FeatureTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const ModalTitle = styled.h3`
  color: #1f2937;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;

  &.full {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
  background: white;

  &:focus {
    border-color: #3b82f6;
  }
`;

const TextArea = styled.textarea`
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 80px;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;


const FormButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;

  &.primary {
    background: #3b82f6;
    color: white;

    &:hover {
      background: #2563eb;
    }
  }

  &.secondary {
    background: #f3f4f6;
    color: #374151;

    &:hover {
      background: #e5e7eb;
    }
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #6b7280;
  padding: 2rem;
  font-style: italic;
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
  margin-bottom: 1rem;
`;

const SuccessMessage = styled.div`
  background: #f0fdf4;
  color: #16a34a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
  margin-bottom: 1rem;
`;


function PaintManagement() {
  const { user } = useAuth();
  
  // Memoize admin check to prevent unnecessary re-renders
  const isAdminUser = useMemo(() => {
    return user?.role === 'admin';
  }, [user?.role]);
  
  const [paints, setPaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [colorFilter, setColorFilter] = useState('');
  const [selectedSurfaceTypes, setSelectedSurfaceTypes] = useState([]);
  const [isSurfaceTypeDropdownOpen, setIsSurfaceTypeDropdownOpen] = useState(false);
  const [environmentFilter, setEnvironmentFilter] = useState('');
  const [finishTypeFilter, setFinishTypeFilter] = useState('');
  const [lineFilter, setLineFilter] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    skip: 0,
    limit: 10,
    hasNext: false,
    hasPrev: false
  });
  const [showModal, setShowModal] = useState(false);
  const [editingPaint, setEditingPaint] = useState(null);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importOptions, setImportOptions] = useState({
    skipDuplicates: true,
    updateExisting: false
  });
  const [importResult, setImportResult] = useState(null);
  const [isImporting, setIsImporting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    color: '',
    surface_types: [],
    environment: 'interno',
    finish_type: 'fosco',
    line: 'standard',
    features: [],
    description: ''
  });


  const fetchPaints = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('skip', pagination.skip.toString());
      params.append('limit', pagination.limit.toString());
      if (searchTerm) params.append('search', searchTerm);
      if (colorFilter) params.append('color', colorFilter);
      if (selectedSurfaceTypes.length > 0) params.append('surface_types', selectedSurfaceTypes.join(','));
      if (environmentFilter) params.append('environment', environmentFilter);
      if (finishTypeFilter) params.append('finish_type', finishTypeFilter);
      if (lineFilter) params.append('line', lineFilter);
      
      const response = await apiClient.get(`${API_ENDPOINTS.PAINTS.LIST}?${params}`);
      setPaints(response.data.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || 0,
        hasNext: response.data.has_next || false,
        hasPrev: response.data.has_prev || false
      }));
    } catch (error) {
      console.error('Error fetching paints:', error);
      setError('Erro ao carregar tintas');
    } finally {
      setLoading(false);
    }
  };

  // Single useEffect for initial load
  useEffect(() => {
    if (isAdminUser) {
      fetchPaints();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdminUser]);

  // useEffect para detectar mudanças no searchTerm
  useEffect(() => {
    if (isAdminUser) {
      fetchPaints();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, colorFilter, selectedSurfaceTypes, environmentFilter, finishTypeFilter, lineFilter, pagination.skip, pagination.limit]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isSurfaceTypeDropdownOpen && !event.target.closest('.multi-select-container')) {
        setIsSurfaceTypeDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isSurfaceTypeDropdownOpen]);


  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Validate surface_types
      if (!formData.surface_types || formData.surface_types.length === 0) {
        setError('Pelo menos um tipo de superfície deve ser selecionado.');
        setLoading(false);
        return;
      }

      const paintData = {
        ...formData
      };

      if (editingPaint) {
        await apiClient.put(API_ENDPOINTS.PAINTS.UPDATE(editingPaint.id), paintData);
        setSuccess('Tinta atualizada com sucesso!');
      } else {
        await apiClient.post(API_ENDPOINTS.PAINTS.CREATE, paintData);
        setSuccess('Tinta criada com sucesso!');
      }

      setShowModal(false);
      resetForm();
      fetchPaints();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar tinta. Tente novamente.');
      console.error('Save paint error:', err);
    } finally {
      setLoading(false);
    }
  };


  const handleEdit = (paint) => {
    setEditingPaint(paint);
    setFormData({
      name: paint.name || '',
      color: paint.color || '',
      surface_types: paint.surface_types || [],
      environment: paint.environment || 'interno',
      finish_type: paint.finish_type || 'fosco',
      line: paint.line || 'standard',
      features: paint.features || [],
      description: paint.description || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (paintId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta tinta?')) return;

    setLoading(true);
    setError(null);
    try {
      await apiClient.delete(API_ENDPOINTS.PAINTS.DELETE(paintId));
      setSuccess('Tinta excluída com sucesso!');
      fetchPaints();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao excluir tinta. Tente novamente.');
      console.error('Delete paint error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const getFeatures = (paint) => {
    return paint.features || [];
  };

  const getSurfaceTypes = (paint) => {
    return paint.surface_types || [];
  };

  // CSV Import functions
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/csv') {
      setImportFile(file);
      setImportResult(null);
    } else {
      setError('Por favor, selecione um arquivo CSV válido.');
    }
  };

  const handleImportOptionsChange = (e) => {
    const { name, checked } = e.target;
    setImportOptions(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
    fetchPaints();
  };

  const handleNextPage = () => {
    if (pagination.hasNext) {
      handlePageChange(pagination.skip + pagination.limit);
    }
  };

  const handlePrevPage = () => {
    if (pagination.hasPrev) {
      handlePageChange(Math.max(0, pagination.skip - pagination.limit));
    }
  };

  const handleSearchChange = (value) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleColorFilterChange = (value) => {
    setColorFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };


  const handleSurfaceTypeToggle = (surfaceType) => {
    setSelectedSurfaceTypes(prev => {
      if (prev.includes(surfaceType)) {
        return prev.filter(type => type !== surfaceType);
      } else {
        return [...prev, surfaceType];
      }
    });
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleRemoveSurfaceType = (surfaceType) => {
    setSelectedSurfaceTypes(prev => prev.filter(type => type !== surfaceType));
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleClearSurfaceTypes = () => {
    setSelectedSurfaceTypes([]);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleEnvironmentFilterChange = (value) => {
    setEnvironmentFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleFinishTypeFilterChange = (value) => {
    setFinishTypeFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const handleLineFilterChange = (value) => {
    setLineFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
  };


  const resetForm = () => {
    setEditingPaint(null);
    setFormData({
      name: '',
      color: '',
      surface_types: [],
      environment: 'interno',
      finish_type: 'fosco',
      line: 'standard',
      features: [],
      description: ''
    });
  };

  const handleImportSubmit = async () => {
    if (!importFile) {
      setError('Por favor, selecione um arquivo CSV.');
      return;
    }

    setIsImporting(true);
    setError(null);
    setImportResult(null);

    try {
      const fileContent = await readFileAsBase64(importFile);
      
      const response = await apiClient.post(API_ENDPOINTS.PAINTS.IMPORT_CSV, {
        file_content: fileContent,
        file_name: importFile.name,
        skip_duplicates: importOptions.skipDuplicates,
        update_existing: importOptions.updateExisting
      });

      setImportResult(response.data);
      
      if (response.data.success) {
        setSuccess(`Importação concluída! ${response.data.message}`);
        // Recarregar a lista de tintas
        fetchPaints();
      } else {
        setError(`Erro na importação: ${response.data.message}`);
      }
    } catch (err) {
      console.error('Erro na importação:', err);
      setError(err.response?.data?.detail || 'Erro ao importar arquivo CSV.');
    } finally {
      setIsImporting(false);
    }
  };

  const readFileAsBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1]; // Remove data:text/csv;base64, prefix
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const downloadCSVTemplate = () => {
    const csvContent = `nome,cor,tipo_parede,ambiente,acabamento,features,linha
Suvinil Toque de Seda,Branco Neve,alvenaria,interno,acetinado,"Lavável, Sem odor, Alta cobertura, Fácil limpeza",premium
Suvinil Fosco Completo,Cinza Urbano,alvenaria,interno/externo,fosco,"Anti-mofo, Alta cobertura, Resistente à umidade",premium
Suvinil Clássica,Amarelo Canário,alvenaria,interno,fosco,"Boa cobertura, Econômica, Rápida secagem",standard
Suvinil Esmalte Sintético,Vermelho Ferrari,"Madeira, Ferro",interno/externo,brilhante,"Alta durabilidade, Resistente ao calor, Impermeável",premium`;

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'template_tintas.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const closeImportModal = () => {
    setShowImportModal(false);
    setImportFile(null);
    setImportResult(null);
    setError(null);
  };

  // Verificar se é admin
  if (!isAdminUser) {
    return (
      <ManagementContainer>
        <ErrorMessage>
          Acesso negado. Apenas administradores podem gerenciar tintas.
        </ErrorMessage>
      </ManagementContainer>
    );
  }

  return (
    <ManagementContainer>
      <Header>
        <Title>Gerenciar Tintas</Title>
        <ButtonGroup>
          <DownloadButton onClick={downloadCSVTemplate}>
            <Download size={20} />
            Baixar Template
          </DownloadButton>
          <ImportButton onClick={() => setShowImportModal(true)}>
            <Upload size={20} />
            Importar CSV
          </ImportButton>
          <AddButton onClick={() => {
            resetForm();
            setShowModal(true);
          }}>
            <Plus size={20} />
            Nova Tinta
          </AddButton>
        </ButtonGroup>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}

      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Buscar tintas..."
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
        <FilterSelect
          value={colorFilter}
          onChange={(e) => handleColorFilterChange(e.target.value)}
        >
          <option value="">Todas as cores</option>
          <option value="branco">Branco</option>
          <option value="preto">Preto</option>
          <option value="azul">Azul</option>
          <option value="vermelho">Vermelho</option>
          <option value="verde">Verde</option>
          <option value="amarelo">Amarelo</option>
          <option value="rosa">Rosa</option>
          <option value="cinza">Cinza</option>
          <option value="marrom">Marrom</option>
          <option value="laranja">Laranja</option>
        </FilterSelect>
        <MultiSelectContainer className="multi-select-container">
          <MultiSelectButton
            type="button"
            onClick={() => setIsSurfaceTypeDropdownOpen(!isSurfaceTypeDropdownOpen)}
          >
            {selectedSurfaceTypes.length > 0 
              ? `${selectedSurfaceTypes.length} tipo(s) selecionado(s)`
              : 'Todos os tipos de superfície'
            }
            <span>{isSurfaceTypeDropdownOpen ? '▲' : '▼'}</span>
          </MultiSelectButton>
          
          {isSurfaceTypeDropdownOpen && (
            <MultiSelectDropdown>
              {[
                { value: 'alvenaria', label: 'Alvenaria' },
                { value: 'madeira', label: 'Madeira' },
                { value: 'ferro', label: 'Ferro' },
                { value: 'concrete', label: 'Concreto' },
                { value: 'metal', label: 'Metal' },
                { value: 'plastic', label: 'Plástico' }
              ].map(option => (
                <MultiSelectOption key={option.value}>
                  <input
                    type="checkbox"
                    checked={selectedSurfaceTypes.includes(option.value)}
                    onChange={() => handleSurfaceTypeToggle(option.value)}
                  />
                  {option.label}
                </MultiSelectOption>
              ))}
              {selectedSurfaceTypes.length > 0 && (
                <MultiSelectOption>
                  <button
                    type="button"
                    onClick={handleClearSurfaceTypes}
                    style={{ 
                      background: 'none', 
                      border: 'none', 
                      color: '#ef4444', 
                      cursor: 'pointer',
                      fontSize: '0.9rem',
                      padding: '0.5rem',
                      width: '100%',
                      textAlign: 'left'
                    }}
                  >
                    Limpar seleção
                  </button>
                </MultiSelectOption>
              )}
            </MultiSelectDropdown>
          )}
          
          {selectedSurfaceTypes.length > 0 && (
            <SelectedTags>
              {selectedSurfaceTypes.map(surfaceType => (
                <SelectedTag key={surfaceType}>
                  {surfaceType}
                  <RemoveTagButton
                    type="button"
                    onClick={() => handleRemoveSurfaceType(surfaceType)}
                  >
                    ×
                  </RemoveTagButton>
                </SelectedTag>
              ))}
            </SelectedTags>
          )}
        </MultiSelectContainer>
        <FilterSelect
          value={environmentFilter}
          onChange={(e) => handleEnvironmentFilterChange(e.target.value)}
        >
          <option value="">Todos os ambientes</option>
          <option value="interno">Interno</option>
          <option value="externo">Externo</option>
          <option value="interno/externo">Interno/Externo</option>
        </FilterSelect>
        <FilterSelect
          value={finishTypeFilter}
          onChange={(e) => handleFinishTypeFilterChange(e.target.value)}
        >
          <option value="">Todos os acabamentos</option>
          <option value="fosco">Fosco</option>
          <option value="acetinado">Acetinado</option>
          <option value="semi-brilhante">Semi-brilhante</option>
          <option value="brilhante">Brilhante</option>
        </FilterSelect>
        <FilterSelect
          value={lineFilter}
          onChange={(e) => handleLineFilterChange(e.target.value)}
        >
          <option value="">Todas as linhas</option>
          <option value="economic">Economic</option>
          <option value="standard">Standard</option>
          <option value="premium">Premium</option>
        </FilterSelect>
        <Button onClick={() => {
          setSearchTerm('');
          setColorFilter('');
          setSelectedSurfaceTypes([]);
          setEnvironmentFilter('');
          setFinishTypeFilter('');
          setLineFilter('');
          setPagination(prev => ({ ...prev, skip: 0 }));
          fetchPaints();
        }}>
          Limpar Filtros
        </Button>
      </SearchContainer>

      {loading ? (
        <LoadingMessage>Carregando tintas...</LoadingMessage>
      ) : (
        <PaintsGrid>
          {paints.map(paint => (
            <PaintCard key={paint.id}>
              <PaintHeader>
                <PaintName>{paint.name}</PaintName>
                <PaintActions>
                  <ActionButton
                    className="edit"
                    onClick={() => handleEdit(paint)}
                    title="Editar"
                  >
                    <Edit size={16} />
                  </ActionButton>
                  <ActionButton
                    className="delete"
                    onClick={() => handleDelete(paint.id)}
                    title="Excluir"
                  >
                    <Trash2 size={16} />
                  </ActionButton>
                </PaintActions>
              </PaintHeader>

              <PaintInfo>
                <InfoRow>
                  <InfoLabel>Cor:</InfoLabel>
                  <InfoValue>{paint.color}</InfoValue>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>Superfície:</InfoLabel>
                  <InfoValue>
                    {getSurfaceTypes(paint).length > 0 ? (
                      <FeaturesContainer>
                        {getSurfaceTypes(paint).map(surfaceType => (
                          <FeatureTag key={surfaceType}>{surfaceType}</FeatureTag>
                        ))}
                      </FeaturesContainer>
                    ) : (
                      'N/A'
                    )}
                  </InfoValue>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>Ambiente:</InfoLabel>
                  <InfoValue>{paint.environment}</InfoValue>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>Acabamento:</InfoLabel>
                  <InfoValue>{paint.finish_type}</InfoValue>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>Linha:</InfoLabel>
                  <InfoValue>{paint.line}</InfoValue>
                </InfoRow>
                {paint.price_per_liter && (
                  <InfoRow>
                    <InfoLabel>Preço/L:</InfoLabel>
                    <InfoValue>R$ {paint.price_per_liter.toFixed(2)}</InfoValue>
                  </InfoRow>
                )}
              </PaintInfo>

              <FeaturesList>
                {getFeatures(paint).map(feature => (
                  <FeatureTag key={feature}>{feature}</FeatureTag>
                ))}
              </FeaturesList>
            </PaintCard>
          ))}
        </PaintsGrid>
      )}

      {paints.length > 0 && (
        <PaginationContainer>
          <PaginationInfo>
            Mostrando {pagination.skip + 1} - {Math.min(pagination.skip + pagination.limit, pagination.total)} de {pagination.total} tintas
          </PaginationInfo>
          <PaginationButtons>
            <PaginationButton 
              onClick={handlePrevPage} 
              disabled={!pagination.hasPrev}
            >
              Anterior
            </PaginationButton>
            <PaginationButton 
              onClick={handleNextPage} 
              disabled={!pagination.hasNext}
            >
              Próximo
            </PaginationButton>
          </PaginationButtons>
        </PaginationContainer>
      )}

      {showModal && (
        <ModalOverlay onClick={() => setShowModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>
                {editingPaint ? 'Editar Tinta' : 'Nova Tinta'}
              </ModalTitle>
              <CloseButton onClick={() => {
                setShowModal(false);
                resetForm();
              }}>
                <X size={20} />
              </CloseButton>
            </ModalHeader>

            <Form onSubmit={handleSubmit}>
              <FormRow>
                <FormGroup>
                  <Label>Nome da Tinta *</Label>
                  <Input
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Cor *</Label>
                  <Input
                    name="color"
                    value={formData.color}
                    onChange={handleInputChange}
                    required
                  />
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>Tipos de Superfície (separados por vírgula) *</Label>
                  <Input
                    name="surface_types"
                    value={formData.surface_types.join(', ')}
                    onChange={(e) => {
                      const surfaceTypes = e.target.value.split(',').map(s => s.trim()).filter(s => s);
                      setFormData(prev => ({ ...prev, surface_types: surfaceTypes }));
                    }}
                    placeholder="Ex: alvenaria, madeira, ferro"
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Ambiente *</Label>
                  <Select
                    name="environment"
                    value={formData.environment}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="interno">Interno</option>
                    <option value="externo">Externo</option>
                    <option value="interno/externo">Interno/Externo</option>
                  </Select>
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>Tipo de Acabamento *</Label>
                  <Select
                    name="finish_type"
                    value={formData.finish_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="fosco">Fosco</option>
                    <option value="acetinado">Acetinado</option>
                    <option value="semi-brilhante">Semi-brilhante</option>
                    <option value="brilhante">Brilhante</option>
                  </Select>
                </FormGroup>
                <FormGroup>
                  <Label>Linha *</Label>
                  <Select
                    name="line"
                    value={formData.line}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="economic">Economic</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                  </Select>
                </FormGroup>
              </FormRow>

              <FormRow>
                <FormGroup>
                  <Label>Features (separadas por vírgula)</Label>
                  <Input
                    name="features"
                    value={formData.features.join(', ')}
                    onChange={(e) => {
                      const features = e.target.value.split(',').map(f => f.trim()).filter(f => f);
                      setFormData(prev => ({ ...prev, features }));
                    }}
                    placeholder="Ex: Lavável, Anti-mofo, Sem odor"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Descrição</Label>
                  <TextArea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                  />
                </FormGroup>
              </FormRow>

              <FormButtonGroup>
                <Button
                  type="button"
                  className="secondary"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  className="primary"
                  disabled={loading}
                >
                  {loading ? 'Salvando...' : (editingPaint ? 'Atualizar' : 'Criar')}
                </Button>
              </FormButtonGroup>
            </Form>
          </ModalContent>
        </ModalOverlay>
      )}

      {/* Import CSV Modal */}
      {showImportModal && (
        <ImportModal>
          <ImportModalContent>
            <ImportModalHeader>
              <ImportModalTitle>Importar Tintas via CSV</ImportModalTitle>
              <CloseButton onClick={closeImportModal}>
                <X size={20} />
              </CloseButton>
            </ImportModalHeader>

            <CSVFormatInfo>
              <CSVFormatTitle>Formato do CSV</CSVFormatTitle>
              <CSVFormatText>
                O arquivo CSV deve conter as seguintes colunas: nome, cor, tipo_parede, ambiente, acabamento, features, linha.
                <br />
                Valores válidos:
                <br />
                • tipo_parede: lista separada por vírgulas (alvenaria, madeira, ferro, concrete, metal, plastic)
                <br />
                • ambiente: interno, externo, interno/externo
                <br />
                • acabamento: fosco, acetinado, brilhante, semi-brilhante
                <br />
                • linha: premium, standard, economic
                <br />
                • features: lista separada por vírgulas (opcional)
              </CSVFormatText>
            </CSVFormatInfo>

            <FileInput
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              placeholder="Selecionar arquivo CSV"
            />

            <ImportOptions>
              <OptionGroup>
                <Checkbox
                  type="checkbox"
                  name="skipDuplicates"
                  checked={importOptions.skipDuplicates}
                  onChange={handleImportOptionsChange}
                />
                <Label>Pular tintas duplicadas</Label>
              </OptionGroup>
              <OptionGroup>
                <Checkbox
                  type="checkbox"
                  name="updateExisting"
                  checked={importOptions.updateExisting}
                  onChange={handleImportOptionsChange}
                />
                <Label>Atualizar tintas existentes</Label>
              </OptionGroup>
            </ImportOptions>

            {importResult && (
              <ImportResult success={importResult.success}>
                <ImportResultTitle success={importResult.success}>
                  {importResult.success ? 'Importação Concluída' : 'Erro na Importação'}
                </ImportResultTitle>
                <ImportResultText success={importResult.success}>
                  {importResult.message}
                </ImportResultText>
                {importResult.result && (
                  <ImportResultText success={importResult.success}>
                    Total de linhas: {importResult.result.total_rows} | 
                    Importadas com sucesso: {importResult.result.successful_imports} | 
                    Falharam: {importResult.result.failed_imports}
                  </ImportResultText>
                )}
                {importResult.errors && importResult.errors.length > 0 && (
                  <ErrorList>
                    {importResult.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ErrorList>
                )}
              </ImportResult>
            )}

            <ImportActions>
              <CancelButton onClick={closeImportModal}>
                Cancelar
              </CancelButton>
              <ImportSubmitButton
                onClick={handleImportSubmit}
                disabled={!importFile || isImporting}
              >
                {isImporting ? (
                  <>
                    <FileText size={20} />
                    Importando...
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    Importar
                  </>
                )}
              </ImportSubmitButton>
            </ImportActions>
          </ImportModalContent>
        </ImportModal>
      )}
    </ManagementContainer>
  );
}

export default PaintManagement;
