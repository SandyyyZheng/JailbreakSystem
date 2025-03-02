import { createStore } from 'vuex'
import axios from 'axios'

// API base URL
const API_URL = 'http://localhost:5000/api'

export default createStore({
  state: {
    attacks: [],
    prompts: [],
    results: [],
    loading: false,
    error: null,
    currentAttack: null,
    currentPrompt: null,
    jailbreakResult: null
  },
  
  getters: {
    getAttackById: (state) => (id) => {
      return state.attacks.find(attack => attack.id === id)
    },
    getPromptById: (state) => (id) => {
      return state.prompts.find(prompt => prompt.id === id)
    },
    getResultById: (state) => (id) => {
      return state.results.find(result => result.id === id)
    },
    getResultsByAttackId: (state) => (attackId) => {
      return state.results.filter(result => result.attack_id === attackId)
    }
  },
  
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_ATTACKS(state, attacks) {
      state.attacks = attacks
    },
    SET_PROMPTS(state, prompts) {
      state.prompts = prompts
    },
    SET_RESULTS(state, results) {
      state.results = results
    },
    SET_CURRENT_ATTACK(state, attack) {
      state.currentAttack = attack
    },
    SET_CURRENT_PROMPT(state, prompt) {
      state.currentPrompt = prompt
    },
    SET_JAILBREAK_RESULT(state, result) {
      state.jailbreakResult = result
    },
    ADD_ATTACK(state, attack) {
      state.attacks.push(attack)
    },
    ADD_PROMPT(state, prompt) {
      state.prompts.push(prompt)
    },
    ADD_RESULT(state, result) {
      state.results.push(result)
    },
    UPDATE_ATTACK(state, updatedAttack) {
      const index = state.attacks.findIndex(attack => attack.id === updatedAttack.id)
      if (index !== -1) {
        state.attacks.splice(index, 1, updatedAttack)
      }
    },
    UPDATE_PROMPT(state, updatedPrompt) {
      const index = state.prompts.findIndex(prompt => prompt.id === updatedPrompt.id)
      if (index !== -1) {
        state.prompts.splice(index, 1, updatedPrompt)
      }
    },
    UPDATE_RESULT(state, updatedResult) {
      const index = state.results.findIndex(result => result.id === updatedResult.id)
      if (index !== -1) {
        state.results.splice(index, 1, updatedResult)
      }
    },
    DELETE_ATTACK(state, attackId) {
      state.attacks = state.attacks.filter(attack => attack.id !== attackId)
    },
    DELETE_PROMPT(state, promptId) {
      state.prompts = state.prompts.filter(prompt => prompt.id !== promptId)
    },
    DELETE_RESULT(state, resultId) {
      state.results = state.results.filter(result => result.id !== resultId)
    }
  },
  
  actions: {
    // Attacks
    async fetchAttacks({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/attacks/`)
        commit('SET_ATTACKS', response.data)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch attacks')
        console.error('Error fetching attacks:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchAttack({ commit }, attackId) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/attacks/${attackId}`)
        commit('SET_CURRENT_ATTACK', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch attack')
        console.error('Error fetching attack:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async createAttack({ commit }, attackData) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${API_URL}/attacks/`, attackData)
        const newAttack = { ...attackData, id: response.data.id }
        commit('ADD_ATTACK', newAttack)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to create attack')
        console.error('Error creating attack:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async updateAttack({ commit }, { attackId, attackData }) {
      commit('SET_LOADING', true)
      try {
        await axios.put(`${API_URL}/attacks/${attackId}`, attackData)
        const updatedAttack = { ...attackData, id: attackId }
        commit('UPDATE_ATTACK', updatedAttack)
        return updatedAttack
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to update attack')
        console.error('Error updating attack:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async deleteAttack({ commit }, attackId) {
      commit('SET_LOADING', true)
      try {
        await axios.delete(`${API_URL}/attacks/${attackId}`)
        commit('DELETE_ATTACK', attackId)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to delete attack')
        console.error('Error deleting attack:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async executeAttack({ commit }, { attackId, prompt }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${API_URL}/attacks/execute`, {
          attack_id: attackId,
          prompt: prompt
        })
        commit('SET_JAILBREAK_RESULT', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to execute attack')
        console.error('Error executing attack:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // Prompts
    async fetchPrompts({ commit }, category = null) {
      commit('SET_LOADING', true)
      try {
        let url = `${API_URL}/prompts/`
        if (category) {
          url += `?category=${category}`
        }
        const response = await axios.get(url)
        commit('SET_PROMPTS', response.data)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch prompts')
        console.error('Error fetching prompts:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchPrompt({ commit }, promptId) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/prompts/${promptId}`)
        commit('SET_CURRENT_PROMPT', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch prompt')
        console.error('Error fetching prompt:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async createPrompt({ commit }, promptData) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${API_URL}/prompts/`, promptData)
        const newPrompt = { ...promptData, id: response.data.id }
        commit('ADD_PROMPT', newPrompt)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to create prompt')
        console.error('Error creating prompt:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async updatePrompt({ commit }, { promptId, promptData }) {
      commit('SET_LOADING', true)
      try {
        await axios.put(`${API_URL}/prompts/${promptId}`, promptData)
        const updatedPrompt = { ...promptData, id: promptId }
        commit('UPDATE_PROMPT', updatedPrompt)
        return updatedPrompt
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to update prompt')
        console.error('Error updating prompt:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async deletePrompt({ commit }, promptId) {
      commit('SET_LOADING', true)
      try {
        await axios.delete(`${API_URL}/prompts/${promptId}`)
        commit('DELETE_PROMPT', promptId)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to delete prompt')
        console.error('Error deleting prompt:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // Results
    async fetchResults({ commit }, attackId = null) {
      commit('SET_LOADING', true)
      try {
        let url = `${API_URL}/results/`
        if (attackId) {
          url += `?attack_id=${attackId}`
        }
        const response = await axios.get(url)
        commit('SET_RESULTS', response.data)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch results')
        console.error('Error fetching results:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async createResult({ commit }, resultData) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${API_URL}/results/`, resultData)
        const newResult = { ...resultData, id: response.data.id }
        commit('ADD_RESULT', newResult)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to create result')
        console.error('Error creating result:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async updateResult({ commit }, { resultId, resultData }) {
      commit('SET_LOADING', true)
      try {
        await axios.put(`${API_URL}/results/${resultId}`, resultData)
        const updatedResult = { ...resultData, id: resultId }
        commit('UPDATE_RESULT', updatedResult)
        return updatedResult
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to update result')
        console.error('Error updating result:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async deleteResult({ commit }, resultId) {
      commit('SET_LOADING', true)
      try {
        await axios.delete(`${API_URL}/results/${resultId}`)
        commit('DELETE_RESULT', resultId)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to delete result')
        console.error('Error deleting result:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchStats({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/results/stats`)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch statistics')
        console.error('Error fetching statistics:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    }
  }
}) 