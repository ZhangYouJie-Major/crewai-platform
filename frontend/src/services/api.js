import http from '../http'

/**
 * API服务类 - 统一管理所有API调用
 */
class ApiService {
  // 认证相关API
  static auth = {
    register: (userData) => http.post('/auth/register/', userData),
    login: (credentials) => http.post('/auth/login/', credentials),
    logout: (refreshToken) => http.post('/auth/logout/', { refresh: refreshToken }),
    refreshToken: (refreshToken) => http.post('/auth/refresh/', { refresh: refreshToken }),
    getCurrentUser: () => http.get('/auth/me/')
  }

  // 用户管理API
  static users = {
    getList: (params = {}) => http.get('/users/', { params }),
    getById: (id) => http.get(`/users/${id}/`),
    create: (userData) => http.post('/users/', userData),
    update: (id, userData) => http.put(`/users/${id}/`, userData),
    delete: (id) => http.delete(`/users/${id}/`),
    getStats: () => http.get('/users/stats/')
  }

  // 角色管理API
  static roles = {
    getList: (params = {}) => http.get('/roles/', { params }),
    getById: (id) => http.get(`/roles/${id}/`),
    create: (roleData) => http.post('/roles/', roleData),
    update: (id, roleData) => http.put(`/roles/${id}/`, roleData),
    delete: (id) => http.delete(`/roles/${id}/`),
    getStats: () => http.get('/roles/stats/')
  }

  // 权限管理API
  static permissions = {
    getList: (params = {}) => http.get('/permissions/', { params }),
    getById: (id) => http.get(`/permissions/${id}/`),
    create: (permissionData) => http.post('/permissions/', permissionData),
    update: (id, permissionData) => http.put(`/permissions/${id}/`, permissionData),
    delete: (id) => http.delete(`/permissions/${id}/`),
    getStats: () => http.get('/permissions/stats/')
  }

  // 用户角色关联API
  static userRoles = {
    getList: (params = {}) => http.get('/user-roles/', { params }),
    assign: (userId, roleId) => http.post('/user-roles/', { user: userId, role: roleId }),
    remove: (id) => http.delete(`/user-roles/${id}/`)
  }

  // 角色权限关联API
  static rolePermissions = {
    getList: (params = {}) => http.get('/role-permissions/', { params }),
    assign: (roleId, permissionId) => http.post('/role-permissions/', { role: roleId, permission: permissionId }),
    remove: (id) => http.delete(`/role-permissions/${id}/`)
  }

  // 仪表盘数据API
  static dashboard = {
    getStats: () => http.get('/dashboard/')
  }
}

export default ApiService