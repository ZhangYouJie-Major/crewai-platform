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

  // LLM模型管理API
  static llmModels = {
    getList: (params = {}) => http.get('/llm-models/', { params }),
    getById: (id) => http.get(`/llm-models/${id}/`),
    create: (modelData) => http.post('/llm-models/', modelData),
    update: (id, modelData) => http.put(`/llm-models/${id}/`, modelData),
    patch: (id, modelData) => http.patch(`/llm-models/${id}/`, modelData),
    delete: (id) => http.delete(`/llm-models/${id}/`),
    testConnection: (modelData) => http.post('/llm-models/test_connection/', modelData),
    validateConnection: (id) => http.post(`/llm-models/${id}/validate_connection/`),
    batchValidate: () => http.post('/llm-models/batch_validate/'),
    getAvailable: () => http.get('/llm-models/available/'),
    getStats: () => http.get('/llm-models/stats/')
  }

  // MCP工具管理API
  static mcpTools = {
    getList: (params = {}) => http.get('/mcp-tools/', { params }),
    getById: (id) => http.get(`/mcp-tools/${id}/`),
    create: (toolData) => http.post('/mcp-tools/', toolData),
    update: (id, toolData) => http.put(`/mcp-tools/${id}/`, toolData),
    delete: (id) => http.delete(`/mcp-tools/${id}/`),
    healthCheck: (id) => http.post(`/mcp-tools/${id}/health-check/`),
    callTool: (id, data) => http.post(`/mcp-tools/${id}/call-tool/`, data),
    getHealthy: () => http.get('/mcp-tools/healthy/'),
    getPublic: () => http.get('/mcp-tools/public/'),
    getStats: () => http.get('/mcp-tools/stats/')
  }

  // CrewAI Agent管理API
  static crewaiAgents = {
    getList: (params = {}) => http.get('/crewai-agents/', { params }),
    getById: (id) => http.get(`/crewai-agents/${id}/`),
    create: (agentData) => http.post('/crewai-agents/', agentData),
    update: (id, agentData) => http.patch(`/crewai-agents/${id}/`, agentData),
    delete: (id) => http.delete(`/crewai-agents/${id}/`),
    start: (id) => http.post(`/crewai-agents/${id}/start/`),
    stop: (id) => http.post(`/crewai-agents/${id}/stop/`),
    pause: (id) => http.post(`/crewai-agents/${id}/pause/`),
    resume: (id) => http.post(`/crewai-agents/${id}/resume/`),
    executeTask: (id, taskData) => http.post(`/crewai-agents/${id}/execute-task/`, taskData),
    getTools: (id) => http.get(`/crewai-agents/${id}/tools/`),
    bindTools: (id, toolData) => http.post(`/crewai-agents/${id}/bind-tools/`, toolData),
    getActive: () => http.get('/crewai-agents/active/'),
    getPublic: () => http.get('/crewai-agents/public/'),
    getStats: () => http.get('/crewai-agents/stats/')
  }

  // Agent-Tool关联管理API
  static agentToolRelations = {
    getList: (params = {}) => http.get('/agent-tool-relations/', { params }),
    getById: (id) => http.get(`/agent-tool-relations/${id}/`),
    create: (relationData) => http.post('/agent-tool-relations/', relationData),
    update: (id, relationData) => http.put(`/agent-tool-relations/${id}/`, relationData),
    delete: (id) => http.delete(`/agent-tool-relations/${id}/`),
    testConnection: (id) => http.post(`/agent-tool-relations/${id}/test-connection/`),
    activate: (id) => http.post(`/agent-tool-relations/${id}/activate/`),
    deactivate: (id) => http.post(`/agent-tool-relations/${id}/deactivate/`),
    getHighUsage: (params = {}) => http.get('/agent-tool-relations/high-usage/', { params }),
    getProblematic: (params = {}) => http.get('/agent-tool-relations/problematic/', { params })
  }

  // 字典管理API
  static dictionaries = {
    getList: (params = {}) => http.get('/dictionaries/', { params }),
    getById: (id) => http.get(`/dictionaries/${id}/`),
    create: (dictionaryData) => http.post('/dictionaries/', dictionaryData),
    update: (id, dictionaryData) => http.put(`/dictionaries/${id}/`, dictionaryData),
    delete: (id) => http.delete(`/dictionaries/${id}/`),
    getChildren: (id) => http.get(`/dictionaries/${id}/children/`),
    getTree: (params = {}) => http.get('/dictionaries/tree/', { params }),
    getOptions: (params = {}) => http.get('/dictionaries/options/', { params }),
    batchCreate: (itemsData) => http.post('/dictionaries/batch_create/', itemsData),
    getStats: () => http.get('/dictionaries/stats/')
  }
}

// 创建代理对象，提供简化的API调用方法
const api = {
  // 认证相关
  register: ApiService.auth.register,
  login: ApiService.auth.login,
  logout: ApiService.auth.logout,
  refreshToken: ApiService.auth.refreshToken,
  getCurrentUser: ApiService.auth.getCurrentUser,
  fetchCurrentUser: ApiService.auth.getCurrentUser, // 别名

  // 用户管理
  getUsers: ApiService.users.getList,
  getUserById: ApiService.users.getById,
  createUser: ApiService.users.create,
  updateUser: ApiService.users.update,
  deleteUser: ApiService.users.delete,
  getUserStats: ApiService.users.getStats,

  // 角色管理
  getRoles: ApiService.roles.getList,
  getRoleById: ApiService.roles.getById,
  createRole: ApiService.roles.create,
  updateRole: ApiService.roles.update,
  deleteRole: ApiService.roles.delete,
  getRoleStats: ApiService.roles.getStats,

  // 权限管理
  getPermissions: ApiService.permissions.getList,
  getPermissionById: ApiService.permissions.getById,
  createPermission: ApiService.permissions.create,
  updatePermission: ApiService.permissions.update,
  deletePermission: ApiService.permissions.delete,
  getPermissionStats: ApiService.permissions.getStats,

  // 用户角色关联
  getUserRoles: ApiService.userRoles.getList,
  assignUserRole: ApiService.userRoles.assign,
  removeUserRole: ApiService.userRoles.remove,

  // 角色权限关联
  getRolePermissions: ApiService.rolePermissions.getList,
  assignRolePermission: ApiService.rolePermissions.assign,
  removeRolePermission: ApiService.rolePermissions.remove,

  // 仪表盘
  getDashboardStats: ApiService.dashboard.getStats,
  fetchDashboardStats: ApiService.dashboard.getStats, // 别名

  // LLM模型管理
  getLLMModels: ApiService.llmModels.getList,
  getLLMModelById: ApiService.llmModels.getById,
  createLLMModel: ApiService.llmModels.create,
  updateLLMModel: ApiService.llmModels.update,
  patchLLMModel: ApiService.llmModels.patch,
  deleteLLMModel: ApiService.llmModels.delete,
  testLLMModelConnection: ApiService.llmModels.testConnection,
  validateLLMModelConnection: ApiService.llmModels.validateConnection,
  batchValidateLLMModels: ApiService.llmModels.batchValidate,
  getAvailableLLMModels: ApiService.llmModels.getAvailable,
  getLLMModelStats: ApiService.llmModels.getStats,

  // MCP工具管理
  getMCPTools: ApiService.mcpTools.getList,
  getMCPToolById: ApiService.mcpTools.getById,
  createMCPTool: ApiService.mcpTools.create,
  updateMCPTool: ApiService.mcpTools.update,
  deleteMCPTool: ApiService.mcpTools.delete,
  healthCheckMCPTool: ApiService.mcpTools.healthCheck,
  callMCPTool: ApiService.mcpTools.callTool,
  getHealthyMCPTools: ApiService.mcpTools.getHealthy,
  getPublicMCPTools: ApiService.mcpTools.getPublic,
  getMCPToolStats: ApiService.mcpTools.getStats,

  // CrewAI Agent管理
  getCrewAIAgents: ApiService.crewaiAgents.getList,
  getCrewAIAgentById: ApiService.crewaiAgents.getById,
  createCrewAIAgent: ApiService.crewaiAgents.create,
  updateCrewAIAgent: ApiService.crewaiAgents.update,
  deleteCrewAIAgent: ApiService.crewaiAgents.delete,
  startCrewAIAgent: ApiService.crewaiAgents.start,
  stopCrewAIAgent: ApiService.crewaiAgents.stop,
  pauseCrewAIAgent: ApiService.crewaiAgents.pause,
  resumeCrewAIAgent: ApiService.crewaiAgents.resume,
  executeCrewAIAgentTask: ApiService.crewaiAgents.executeTask,
  getCrewAIAgentTools: ApiService.crewaiAgents.getTools,
  bindCrewAIAgentTools: ApiService.crewaiAgents.bindTools,
  getActiveCrewAIAgents: ApiService.crewaiAgents.getActive,
  getPublicCrewAIAgents: ApiService.crewaiAgents.getPublic,
  getCrewAIAgentStats: ApiService.crewaiAgents.getStats,

  // Agent-Tool关联管理
  getAgentToolRelations: ApiService.agentToolRelations.getList,
  getAgentToolRelationById: ApiService.agentToolRelations.getById,
  createAgentToolRelation: ApiService.agentToolRelations.create,
  updateAgentToolRelation: ApiService.agentToolRelations.update,
  deleteAgentToolRelation: ApiService.agentToolRelations.delete,
  testAgentToolConnection: ApiService.agentToolRelations.testConnection,
  activateAgentToolRelation: ApiService.agentToolRelations.activate,
  deactivateAgentToolRelation: ApiService.agentToolRelations.deactivate,
  getHighUsageAgentToolRelations: ApiService.agentToolRelations.getHighUsage,
  getProblematicAgentToolRelations: ApiService.agentToolRelations.getProblematic,

  // 字典管理
  getDictionaries: ApiService.dictionaries.getList,
  getDictionaryById: ApiService.dictionaries.getById,
  createDictionary: ApiService.dictionaries.create,
  updateDictionary: ApiService.dictionaries.update,
  deleteDictionary: ApiService.dictionaries.delete,
  getDictionaryChildren: ApiService.dictionaries.getChildren,
  getDictionaryTree: ApiService.dictionaries.getTree,
  getDictionaryOptions: ApiService.dictionaries.getOptions,
  batchCreateDictionaries: ApiService.dictionaries.batchCreate,
  getDictionaryStats: ApiService.dictionaries.getStats
}

export { ApiService }
export default api