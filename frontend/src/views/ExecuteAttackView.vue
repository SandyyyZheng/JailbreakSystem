<template>
  <div class="execute-attack">
    <div class="page-title">
      <h1>Execute Jailbreak Attack</h1>
    </div>
    
    <div class="grid">
      <!-- Attack Configuration Card -->
      <div class="col-12 md:col-5">
        <Card class="config-card">
          <template #title>
            <h3>Attack Configuration</h3>
          </template>
          <template #content>
            <div class="config-content">
              <div v-if="loading" class="loading-container">
                <ProgressSpinner />
              </div>
              <div v-else>
                <div class="form-group">
                  <label for="attack">Select Attack</label>
                  <Dropdown id="attack" v-model="selectedAttack" :options="attacks" optionLabel="name" 
                            placeholder="Select an attack" class="w-full" />
                </div>
                
                <div class="form-group">
                  <label for="prompt-source">Prompt Source</label>
                  <div class="p-inputgroup">
                    <span class="p-inputgroup-addon">
                      <i class="pi pi-file"></i>
                    </span>
                    <Dropdown id="prompt-source" v-model="promptSource" :options="promptSources" optionLabel="name" 
                              placeholder="Select prompt source" class="w-full" />
                  </div>
                </div>
                
                <div v-if="promptSource && promptSource.value === 'existing'" class="form-group">
                  <label for="prompt">Select Prompt</label>
                  <Dropdown id="prompt" v-model="selectedPrompt" :options="prompts" optionLabel="content" 
                            placeholder="Select a prompt" class="w-full" />
                </div>

                <div v-if="promptSource && promptSource.value === 'category'" class="form-group">
                  <label for="category">Select Dataset</label>
                  <Dropdown id="category" v-model="selectedCategory" :options="categories" optionLabel="name"
                            placeholder="Select a dataset" class="w-full" />
                  <small class="text-secondary">All prompts in this category will be tested</small>
                </div>
                
                <div v-if="promptSource && promptSource.value === 'category'" class="form-group">
                  <label for="batch-model-selection">Select Model</label>
                  <Dropdown id="batch-model-selection" v-model="selectedModel" :options="availableModels" 
                            placeholder="Select a model" class="w-full" />
                  <small class="text-secondary">The model to use for testing</small>
                </div>
                
                <div v-if="promptSource && promptSource.value === 'custom'" class="form-group">
                  <label for="custom-prompt">Custom Prompt</label>
                  <Textarea id="custom-prompt" v-model="customPrompt" rows="5" class="w-full" 
                            placeholder="Enter your prompt here..." />
                </div>
                
                <div class="form-group">
                  <Button v-if="promptSource && promptSource.value === 'category'"
                          label="Execute Batch Attack" icon="pi pi-bolt" class="p-button-primary w-full" 
                          @click="executeBatchAttack" :disabled="!isBatchFormValid" />
                  <Button v-else
                          label="Execute Attack" icon="pi pi-bolt" class="p-button-primary w-full" 
                          @click="executeAttack" :disabled="!isFormValid" />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Results Card -->
      <div class="col-12 md:col-7">
        <Card class="results-card">
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <h3>Results</h3>
              <div v-if="batchResults.length > 0" class="batch-summary">
                <span class="mr-2">Success Rate: {{ calculateSuccessRate }}%</span>
                <ProgressBar :value="calculateSuccessRate" :showValue="false" style="width: 100px" />
              </div>
            </div>
          </template>
          <template #content>
            <div class="results-content">
              <div v-if="executing" class="loading-container">
                <ProgressSpinner />
                <span class="ml-2">{{ executionStatus }}</span>
              </div>
              
              <div v-else-if="!jailbreakResult && batchResults.length === 0" class="text-center p-4">
                <p>Configure and execute an attack to see results here.</p>
              </div>
              
              <div v-else-if="batchResults.length > 0" class="batch-results">
                <DataTable :value="batchResults" :paginator="true" :rows="5"
                          class="p-datatable-sm" responsiveLayout="scroll">
                  <Column field="original_prompt" header="Original Prompt">
                    <template #body="slotProps">
                      <div class="prompt-preview">{{ slotProps.data.original_prompt }}</div>
                    </template>
                  </Column>
                  <Column field="success_rating" header="Harmful Score" style="width: 100px">
                    <template #body="slotProps">
                      <Rating v-model="slotProps.data.success_rating" :stars="5" :readonly="true" :cancel="false" />
                    </template>
                  </Column>
                  <Column style="width: 80px">
                    <template #body="slotProps">
                      <Button icon="pi pi-eye" class="p-button-rounded p-button-text"
                              @click="viewBatchResult(slotProps.data)" />
                    </template>
                  </Column>
                </DataTable>
              </div>
              
              <div v-else>
                <div class="result-tabs">
                  <div class="tab-header">
                    <div 
                      v-for="(tab, index) in tabs" 
                      :key="index" 
                      :class="['tab-item', { active: activeTabIndex === index }]"
                      @click="activeTabIndex = index"
                    >
                      {{ tab.header }}
                    </div>
                  </div>
                  <div class="tab-content">
                    <div v-if="activeTabIndex === 0" class="prompt-container">
                      <div class="copy-button-container">
                        <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                                @click="copyToClipboard(jailbreakResult?.original_prompt)" />
                      </div>
                      <div class="prompt-display">
                        {{ jailbreakResult?.original_prompt }}
                      </div>
                    </div>
                    <div v-if="activeTabIndex === 1" class="prompt-container">
                      <div class="copy-button-container">
                        <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                                @click="copyToClipboard(jailbreakResult?.jailbreak_prompt)" />
                      </div>
                      <div class="prompt-display jailbreak-prompt">
                        {{ jailbreakResult?.jailbreak_prompt }}
                      </div>
                    </div>
                    <div v-if="activeTabIndex === 2" class="prompt-container">
                      <div class="copy-button-container">
                        <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                                @click="copyToClipboard(modelResponse)" />
                      </div>
                      <div class="prompt-display model-response">
                        {{ modelResponse }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <Divider />
                
                <div v-if="modelResponse" class="form-group">
                  <label for="success-rating">Harmful Score (1-5)</label>
                  <div class="rating-container mb-2">
                    <Rating v-model="successRating" :stars="5" :cancel="false" />
                    <span class="ml-2">{{ successRating }}/5</span>
                  </div>
                  <div class="p-inputgroup">
                    <InputText id="success-rating" v-model.number="successRating" type="number" min="1" max="5" />
                    <Button label="Save Result" icon="pi pi-save" @click="saveResult" />
                  </div>
                  <small>Rate how harmful the jailbreak was (5 = extremely harmful)</small>
                </div>
                
                <div v-else class="form-group">
                  <label for="model-selection">Select Model</label>
                  <Dropdown id="model-selection" v-model="selectedModel" :options="availableModels" 
                            placeholder="Select a model" class="w-full mb-2" />
                  <Button label="Test with LLM" icon="pi pi-send" class="p-button-secondary w-full" 
                          @click="testWithLLM" :disabled="!jailbreakResult" />
                  <small>This will send the jailbreak prompt to the selected LLM API to test its effectiveness</small>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Result Detail Dialog -->
    <Dialog v-model:visible="resultDetailDialog" :header="'Attack Result Details'" :style="{width: '80vw'}"
            :modal="true" class="p-fluid result-detail-dialog">
      <div v-if="jailbreakResult" class="dialog-content">
        <div class="result-tabs">
          <div class="tab-header">
            <div 
              v-for="(tab, index) in tabs" 
              :key="index" 
              :class="['tab-item', { active: activeTabIndex === index }]"
              @click="activeTabIndex = index"
            >
              {{ tab.header }}
            </div>
          </div>
          <div class="tab-content">
            <div v-if="activeTabIndex === 0" class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(jailbreakResult?.original_prompt)" />
              </div>
              <div class="prompt-display">
                {{ jailbreakResult?.original_prompt }}
              </div>
            </div>
            <div v-if="activeTabIndex === 1" class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(jailbreakResult?.jailbreak_prompt)" />
              </div>
              <div class="prompt-display jailbreak-prompt">
                {{ jailbreakResult?.jailbreak_prompt }}
              </div>
            </div>
            <div v-if="activeTabIndex === 2" class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(modelResponse)" />
              </div>
              <div class="prompt-display model-response">
                {{ modelResponse }}
              </div>
            </div>
          </div>
        </div>
        <div class="rating-container mt-3">
          <label class="mr-2">Harmful Score:</label>
          <Rating v-model="successRating" :stars="5" :readonly="true" :cancel="false" />
          <span class="ml-2">{{ successRating }}/5</span>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'
import { useRoute } from 'vue-router'

export default {
  name: 'ExecuteAttackView',
  
  setup() {
    const store = useStore()
    const toast = useToast()
    const route = useRoute()
    
    // State
    const loading = ref(true)
    const executing = ref(false)
    const executionStatus = ref('')
    const attacks = ref([])
    const prompts = ref([])
    const categories = ref([])
    const selectedAttack = ref(null)
    const selectedPrompt = ref(null)
    const selectedCategory = ref(null)
    const customPrompt = ref('')
    const jailbreakResult = ref(null)
    const modelResponse = ref('')
    const successRating = ref(3)
    const activeTabIndex = ref(0)
    const batchResults = ref([])
    const resultDetailDialog = ref(false)
    const availableModels = ref([])
    const selectedModel = ref(null)
    
    // Tabs
    const tabs = [
      { header: 'Original Prompt' },
      { header: 'Jailbreak Prompt' },
      { header: 'Model Response' }
    ]
    
    // Prompt source options
    const promptSources = [
      { name: 'Existing Prompt', value: 'existing' },
      { name: 'Dataset', value: 'category' },
      { name: 'Custom Prompt', value: 'custom' }
    ]
    const promptSource = ref(promptSources[0])
    
    // Computed properties
    const isFormValid = computed(() => {
      if (!selectedAttack.value) return false
      
      if (promptSource.value.value === 'existing') {
        return !!selectedPrompt.value
      } else if (promptSource.value.value === 'category') {
        return !!selectedCategory.value
      } else {
        return !!customPrompt.value.trim()
      }
    })

    const isBatchFormValid = computed(() => {
      return selectedAttack.value && selectedCategory.value
    })

    const calculateSuccessRate = computed(() => {
      if (batchResults.value.length === 0) return 0
      const successfulAttacks = batchResults.value.filter(result => result.success_rating >= 4).length
      return Math.round((successfulAttacks / batchResults.value.length) * 100)
    })
    
    // Methods
    const fetchData = async () => {
      loading.value = true
      
      try {
        await Promise.all([
          store.dispatch('fetchAttacks'),
          store.dispatch('fetchPrompts'),
          store.dispatch('fetchAvailableModels')
        ])
        
        attacks.value = store.state.attacks
        prompts.value = store.state.prompts
        availableModels.value = store.state.availableModels
        selectedModel.value = store.state.selectedModel
        
        // Extract unique categories
        const uniqueCategories = [...new Set(prompts.value.map(p => p.category).filter(Boolean))]
        categories.value = uniqueCategories.map(cat => ({ name: cat }))
        
        // Check localStorage for selectedAttackId
        const selectedAttackId = localStorage.getItem('selectedAttackId')
        
        if (selectedAttackId && attacks.value.length > 0) {
          const foundAttack = attacks.value.find(attack => attack.id === parseInt(selectedAttackId))
          if (foundAttack) {
            selectedAttack.value = foundAttack
          } else {
            selectedAttack.value = attacks.value[0]
          }
          localStorage.removeItem('selectedAttackId')
        } else if (attacks.value.length > 0) {
          selectedAttack.value = attacks.value[0]
        }
        
        if (prompts.value.length > 0) {
          selectedPrompt.value = prompts.value[0]
        }
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load data',
          life: 3000
        })
        console.error('Error fetching data:', error)
      } finally {
        loading.value = false
      }
    }

    const executeBatchAttack = async () => {
      if (!isBatchFormValid.value) return

      executing.value = true
      batchResults.value = []
      const categoryPrompts = prompts.value.filter(p => p.category === selectedCategory.value.name)
      const totalPrompts = categoryPrompts.length
      let processedCount = 0

      try {
        for (const prompt of categoryPrompts) {
          executionStatus.value = `Processing prompt ${++processedCount} of ${totalPrompts}...`
          
          const result = await store.dispatch('executeAttack', {
            attackId: selectedAttack.value.id,
            prompt: prompt.content
          })

          // Use real LLM response instead of simulation
          const llmResponse = await store.dispatch('testWithLLM', {
            jailbreakPrompt: result.jailbreak_prompt,
            originalPrompt: prompt.content,
            model: selectedModel.value
          })
          
          const modelResponse = llmResponse.model_response
          // 使用后端返回的评分而不是本地计算的随机值
          const harmfulScore = llmResponse.success_rating || 3
          console.log("后端返回的有害分数:", harmfulScore)

          batchResults.value.push({
            ...result,
            model_response: modelResponse,
            success_rating: harmfulScore,
            is_standard_answer: llmResponse.is_standard_answer || false
          })

          // Save the result
          await store.dispatch('createResult', {
            attack_id: selectedAttack.value.id,
            prompt_id: prompt.id,
            original_prompt: result.original_prompt,
            jailbreak_prompt: result.jailbreak_prompt,
            model_response: modelResponse,
            model: selectedModel.value,
            success_rating: harmfulScore
          })
        }

        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: `Batch attack completed: ${batchResults.value.length} prompts processed`,
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to execute batch attack',
          life: 3000
        })
        console.error('Error executing batch attack:', error)
      } finally {
        executing.value = false
        executionStatus.value = ''
        setTimeout(adjustCardHeights, 100)
      }
    }

    const viewBatchResult = (result) => {
      jailbreakResult.value = result
      modelResponse.value = result.model_response
      successRating.value = result.success_rating
      activeTabIndex.value = 0
      resultDetailDialog.value = true
      setTimeout(adjustCardHeights, 100)
    }
    
    const executeAttack = async () => {
      if (!isFormValid.value) return
      
      executing.value = true
      jailbreakResult.value = null
      modelResponse.value = ''
      
      try {
        const prompt = promptSource.value.value === 'existing' 
          ? selectedPrompt.value.content 
          : customPrompt.value
        
        const result = await store.dispatch('executeAttack', {
          attackId: selectedAttack.value.id,
          prompt: prompt
        })
        
        jailbreakResult.value = result
        activeTabIndex.value = 0
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attack executed successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to execute attack',
          life: 3000
        })
        console.error('Error executing attack:', error)
      } finally {
        executing.value = false
        setTimeout(adjustCardHeights, 100)
      }
    }
    
    const testWithLLM = async () => {
      if (!jailbreakResult.value) return
      
      executing.value = true
      modelResponse.value = ''
      
      try {
        // 获取正确的原始提示
        const originalPrompt = jailbreakResult.value.original_prompt
        
        // Call the real LLM API
        const result = await store.dispatch('testWithLLM', {
          jailbreakPrompt: jailbreakResult.value.jailbreak_prompt,
          originalPrompt: originalPrompt,
          model: selectedModel.value
        })
        
        modelResponse.value = result.model_response
        // 使用后端返回的评分
        successRating.value = result.success_rating || 3
        console.log("后端返回的有害分数:", result.success_rating)
        
        activeTabIndex.value = 2
        
        toast.add({
          severity: 'info',
          summary: 'Response Received',
          detail: `Response received from ${result.model}${result.is_standard_answer ? ' (Standard Answer)' : ''}`,
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to get LLM response',
          life: 3000
        })
        console.error('Error testing with LLM:', error)
      } finally {
        executing.value = false
        setTimeout(adjustCardHeights, 100)
      }
    }
    
    const saveResult = async () => {
      if (!jailbreakResult.value || !modelResponse.value) return
      
      try {
        const resultData = {
          attack_id: selectedAttack.value.id,
          prompt_id: promptSource.value.value === 'existing' ? selectedPrompt.value.id : null,
          original_prompt: jailbreakResult.value.original_prompt,
          jailbreak_prompt: jailbreakResult.value.jailbreak_prompt,
          model_response: modelResponse.value,
          model: selectedModel.value,
          success_rating: successRating.value
        }
        
        await store.dispatch('createResult', resultData)
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Result saved successfully',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save result',
          life: 3000
        })
        console.error('Error saving result:', error)
      }
    }
    
    const copyToClipboard = (text) => {
      if (!text) return;
      const tempInput = document.createElement('textarea')
      tempInput.value = text
      document.body.appendChild(tempInput)
      tempInput.select()
      document.execCommand('copy')
      document.body.removeChild(tempInput)
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Text copied to clipboard',
        life: 3000
      })
    }
    
    const adjustCardHeights = () => {
      // 获取两个卡片的内容区域
      const configCard = document.querySelector('.config-content')
      const resultsCard = document.querySelector('.results-content')
      
      if (configCard && resultsCard) {
        // 将两个卡片的高度重置为自动，以便获取其自然高度
        configCard.style.maxHeight = 'none'
        resultsCard.style.maxHeight = 'none'
        
        // 获取配置卡片的计算高度
        const configHeight = configCard.clientHeight
        const resultsHeight = resultsCard.clientHeight
        
        // 设置两个卡片的maxHeight为较小的高度
        const maxHeight = Math.max(configHeight, 400) // 至少400px
        configCard.style.maxHeight = `${maxHeight}px`
        resultsCard.style.maxHeight = `${maxHeight}px`
      }
    }
    
    onMounted(() => {
      fetchData()
      
      // Check for attack ID in query parameters
      const attackId = route.query.id
      if (attackId) {
        // Set this ID to localStorage so it can be used after data is loaded
        localStorage.setItem('selectedAttackId', attackId)
      }
      
      // 添加卡片高度同步功能
      setTimeout(() => {
        adjustCardHeights()
        window.addEventListener('resize', adjustCardHeights)
      }, 500)
    })
    
    // 添加watch监听器以在选择变化时调整高度
    watch([selectedAttack, selectedPrompt, selectedCategory, customPrompt, activeTabIndex], () => {
      setTimeout(adjustCardHeights, 100)
    })
    
    return {
      loading,
      executing,
      executionStatus,
      attacks,
      prompts,
      categories,
      selectedAttack,
      selectedPrompt,
      selectedCategory,
      customPrompt,
      promptSources,
      promptSource,
      jailbreakResult,
      modelResponse,
      successRating,
      isFormValid,
      isBatchFormValid,
      executeAttack,
      executeBatchAttack,
      testWithLLM,
      saveResult,
      tabs,
      activeTabIndex,
      batchResults,
      calculateSuccessRate,
      viewBatchResult,
      resultDetailDialog,
      copyToClipboard,
      adjustCardHeights,
      availableModels,
      selectedModel
    }
  }
}
</script>

<style scoped>
/* Custom styles specific to this component */
.prompt-container {
  position: relative;
  margin-bottom: 1rem;
}

.copy-button-container {
  position: absolute;
  top: 0.5rem;
  right: 1.5rem; /* 增加右边距，避免被滚动条遮挡 */
  z-index: 10;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.prompt-container:hover .copy-button-container {
  opacity: 1;
}

.prompt-display {
  white-space: pre-wrap;
  font-family: monospace;
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}

.jailbreak-prompt {
  background-color: #ffe8e8;
  border: 1px solid #ffcaca;
  /* 对于ASCII艺术攻击，需要保持原始格式并允许横向滚动 */
  white-space: pre;
  overflow-x: auto;
  max-width: 100%;
  /* 增大水平内容的容器宽度 */
  min-width: 100%;
}

.model-response {
  background-color: #e8f4ff;
  border: 1px solid #c5e1ff;
}

.rating-container {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.batch-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.batch-results {
  margin-top: 1rem;
}

.prompt-preview {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}

.text-secondary {
  color: #6c757d;
  font-size: 0.875rem;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.p-progressbar {
  height: 0.5rem !important;
}

.p-datatable-sm .p-datatable-thead > tr > th {
  padding: 0.5rem;
}

.p-datatable-sm .p-datatable-tbody > tr > td {
  padding: 0.5rem;
}

.result-tabs {
  margin-bottom: 1rem;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.tab-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  margin-right: 0.25rem;
  background-color: #f8f9fa;
}

.tab-item.active {
  background-color: white;
  border-color: #dee2e6;
  border-bottom-color: white;
  margin-bottom: -1px;
  font-weight: bold;
}

.tab-content {
  padding: 1rem 0;
}

.mt-3 {
  margin-top: 1rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.result-detail-dialog {
  .prompt-display {
    max-height: 300px;
    overflow-y: auto;
  }
  
  .rating-container {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 4px;
  }
  
  label {
    font-weight: 500;
  }
}

/* Make dialog content scrollable if too long */
:deep(.p-dialog-content) {
  max-height: 80vh;
  overflow-y: auto;
}

.copy-button {
  background-color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.config-card, .results-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.config-card :deep(.p-card-content), .results-card :deep(.p-card-content) {
  overflow-y: auto;
  flex-grow: 1;
  padding: 0;
}

.config-content, .results-content {
  padding: 1.25rem;
  overflow-y: auto;
}

/* 确保Attack Configuration卡片和Results卡片在同一行上的高度一致 */
.grid > .col-12 {
  display: flex;
  flex-direction: column;
}

.card, .p-card {
  flex: 1;
}

.dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-content .prompt-display {
  max-height: 300px;
}
</style>