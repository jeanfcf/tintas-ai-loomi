import React, { useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { Plus, Edit, Trash2, Users } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import apiClient, { API_ENDPOINTS } from '../config/api';

const Container = styled.div`
  padding: 1rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h2`
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Button = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
`;

const Input = styled.input`
  flex: 1;
  min-width: 200px;
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

const FilterSelect = styled.select`
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  outline: none;
  font-size: 0.9rem;
  background: white;
  min-width: 150px;

  &:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
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
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.thead`
  background: #f9fafb;
`;

const TableHeaderCell = styled.th`
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s;

  &:hover {
    background: #f9fafb;
  }

  &:last-child {
    border-bottom: none;
  }
`;

const TableCell = styled.td`
  padding: 1rem;
  color: #374151;
`;

const RoleBadge = styled.span`
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: ${props => {
    switch (props.role) {
      case 'admin': return '#fef3c7';
      case 'user': return '#dbeafe';
      default: return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.role) {
      case 'admin': return '#92400e';
      case 'user': return '#1e40af';
      default: return '#6b7280';
    }
  }};
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  color: #6b7280;
  transition: all 0.2s;
  margin: 0 0.25rem;

  &:hover {
    background: #f3f4f6;
    color: #374151;
  }

  &.edit:hover {
    color: #3b82f6;
  }

  &.delete:hover {
    color: #dc2626;
  }
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
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background 0.2s;

  &:hover {
    background: #f3f4f6;
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
`;

const FormInput = styled.input`
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
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
  border: 1px solid #fecaca;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  color: #6b7280;
`;

function UserManagement() {
  const { isAdmin } = useAuth();
  
  // Memoize admin check to prevent unnecessary re-renders
  const isAdminUser = useMemo(() => {
    return isAdmin();
  }, [isAdmin]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    skip: 0,
    limit: 10,
    hasNext: false,
    hasPrev: false
  });
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    role: 'user',
    status: 'active'
  });
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('skip', pagination.skip.toString());
      params.append('limit', pagination.limit.toString());
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);
      if (statusFilter) params.append('status', statusFilter);
      
      const response = await apiClient.get(`${API_ENDPOINTS.USERS.LIST}?${params}`);
      setUsers(response.data.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || 0,
        hasNext: response.data.has_next || false,
        hasPrev: response.data.has_prev || false
      }));
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  // Single useEffect for initial load
  useEffect(() => {
    if (isAdminUser) {
      fetchUsers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdminUser]);

  const handleCreateUser = () => {
    setEditingUser(null);
    setFormData({
      email: '',
      username: '',
      password: '',
      full_name: '',
      role: 'user',
      status: 'active'
    });
    setShowModal(true);
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      username: user.username,
      password: '',
      full_name: user.full_name,
      role: user.role,
      status: user.status
    });
    setShowModal(true);
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Tem certeza que deseja deletar este usuário?')) {
      try {
        await apiClient.delete(API_ENDPOINTS.USERS.DELETE(userId));
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        setError('Erro ao deletar usuário');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingUser) {
        // Update user
        const updateData = { ...formData };
        console.log('🔍 Form data before processing:', formData);
        console.log('🔍 Password field value:', formData.password);
        
        // Only remove password if it's empty for update (allow password change)
        if (!updateData.password || updateData.password.trim() === '') {
          console.log('🚫 Removing password field (empty)');
          delete updateData.password;
        } else {
          console.log('✅ Keeping password field for update');
        }
        
        console.log('📤 Sending update data:', updateData);
        await apiClient.put(API_ENDPOINTS.USERS.UPDATE(editingUser.id), updateData);
      } else {
        // Create user - password is required
        console.log('📤 Creating new user with data:', formData);
        await apiClient.post(API_ENDPOINTS.USERS.CREATE, formData);
      }
      
      setShowModal(false);
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      setError(error.response?.data?.detail || 'Erro ao salvar usuário');
    }
  };

  // Remove local filtering since we're now filtering on the backend

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
    fetchUsers();
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
    fetchUsers();
  };

  const handleRoleFilterChange = (value) => {
    setRoleFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
    fetchUsers();
  };

  const handleStatusFilterChange = (value) => {
    setStatusFilter(value);
    setPagination(prev => ({ ...prev, skip: 0 }));
    fetchUsers();
  };

  if (!isAdminUser) {
    return (
      <Container>
        <ErrorMessage>
          Acesso negado. Apenas administradores podem gerenciar usuários.
        </ErrorMessage>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container>
        <LoadingSpinner>Carregando usuários...</LoadingSpinner>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>
          <Users size={24} />
          Gerenciar Usuários
        </Title>
        <Button onClick={handleCreateUser}>
          <Plus size={16} />
          Novo Usuário
        </Button>
      </Header>

      <SearchBar>
        <Input
          type="text"
          placeholder="Buscar usuários..."
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
        <FilterSelect
          value={roleFilter}
          onChange={(e) => handleRoleFilterChange(e.target.value)}
        >
          <option value="">Todos os roles</option>
          <option value="user">Usuário</option>
          <option value="admin">Admin</option>
        </FilterSelect>
        <FilterSelect
          value={statusFilter}
          onChange={(e) => handleStatusFilterChange(e.target.value)}
        >
          <option value="">Todos os status</option>
          <option value="active">Ativo</option>
          <option value="inactive">Inativo</option>
          <option value="suspended">Suspenso</option>
        </FilterSelect>
      </SearchBar>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      <Table>
        <TableHeader>
          <tr>
            <TableHeaderCell>Nome</TableHeaderCell>
            <TableHeaderCell>Username</TableHeaderCell>
            <TableHeaderCell>Email</TableHeaderCell>
            <TableHeaderCell>Role</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Ações</TableHeaderCell>
          </tr>
        </TableHeader>
        <TableBody>
          {users.map(user => (
            <TableRow key={user.id}>
              <TableCell>{user.full_name}</TableCell>
              <TableCell>{user.username}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>
                <RoleBadge role={user.role}>
                  {user.role}
                </RoleBadge>
              </TableCell>
              <TableCell>
                <RoleBadge role={user.status}>
                  {user.status}
                </RoleBadge>
              </TableCell>
              <TableCell>
                <ActionButton
                  className="edit"
                  onClick={() => handleEditUser(user)}
                  title="Editar usuário"
                >
                  <Edit size={16} />
                </ActionButton>
                <ActionButton
                  className="delete"
                  onClick={() => handleDeleteUser(user.id)}
                  title="Deletar usuário"
                >
                  <Trash2 size={16} />
                </ActionButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <PaginationContainer>
        <PaginationInfo>
          Mostrando {pagination.skip + 1} - {Math.min(pagination.skip + pagination.limit, pagination.total)} de {pagination.total} usuários
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

      {showModal && (
        <ModalOverlay onClick={() => setShowModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={() => setShowModal(false)}>
              ×
            </CloseButton>
            
            <h3>{editingUser ? 'Editar Usuário' : 'Novo Usuário'}</h3>
            
            <Form onSubmit={handleSubmit}>
              <FormGroup>
                <Label>Email</Label>
                <FormInput
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Username</Label>
                <FormInput
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Nome Completo</Label>
                <FormInput
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Senha {editingUser && '(deixe em branco para manter a atual)'}</Label>
                <FormInput
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required={!editingUser}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Role</Label>
                <Select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="user">Usuário</option>
                  <option value="admin">Administrador</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                >
                  <option value="active">Ativo</option>
                  <option value="inactive">Inativo</option>
                  <option value="suspended">Suspenso</option>
                </Select>
              </FormGroup>
              
              <Button type="submit">
                {editingUser ? 'Atualizar' : 'Criar'} Usuário
              </Button>
            </Form>
          </ModalContent>
        </ModalOverlay>
      )}
    </Container>
  );
}

export default UserManagement;
