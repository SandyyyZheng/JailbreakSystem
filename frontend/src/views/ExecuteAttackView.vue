<template>
  <div class="execute-attack">
    <div class="page-title">
      <h1>Execute Jailbreak Attack</h1>
    </div>
    
    <div class="grid">
      <!-- Attack Configuration Card -->
      <div class="col-12 md:col-5">
        <Card>
          <template #title>
            <h3>Attack Configuration</h3>
          </template>
          <template #content>
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
              
              <div v-if="promptSource && promptSource.value === 'custom'" class="form-group">
                <label for="custom-prompt">Custom Prompt</label>
                <Textarea id="custom-prompt" v-model="customPrompt" rows="5" class="w-full" 
                          placeholder="Enter your prompt here..." />
              </div>
              
              <div class="form-group">
                <Button label="Execute Attack" icon="pi pi-bolt" class="p-button-primary w-full" 
                        @click="executeAttack" :disabled="!isFormValid" />
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Results Card -->
      <div class="col-12 md:col-7">
        <Card>
          <template #title>
            <h3>Results</h3>
          </template>
          <template #content>
            <div v-if="executing" class="loading-container">
              <ProgressSpinner />
              <span class="ml-2">Executing attack...</span>
            </div>
            
            <div v-else-if="!jailbreakResult" class="text-center p-4">
              <p>Configure and execute an attack to see results here.</p>
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
                  <div v-if="activeTabIndex === 0" class="prompt-display">
                    {{ jailbreakResult.original_prompt }}
                  </div>
                  <div v-if="activeTabIndex === 1" class="prompt-display jailbreak-prompt">
                    {{ jailbreakResult.jailbreak_prompt }}
                  </div>
                  <div v-if="activeTabIndex === 2 && modelResponse" class="prompt-display model-response">
                    {{ modelResponse }}
                  </div>
                </div>
              </div>
              
              <Divider />
              
              <div v-if="modelResponse" class="form-group">
                <label for="success-rating">Success Rating (1-10)</label>
                <div class="p-inputgroup">
                  <InputText id="success-rating" v-model.number="successRating" type="number" min="1" max="10" />
                  <Button label="Save Result" icon="pi pi-save" @click="saveResult" />
                </div>
                <small>Rate how successful the jailbreak was (10 = completely successful)</small>
              </div>
              
              <div v-else class="form-group">
                <Button label="Test with LLM" icon="pi pi-send" class="p-button-secondary w-full" 
                        @click="testWithLLM" :disabled="!jailbreakResult" />
                <small>This will send the jailbreak prompt to an LLM API to test its effectiveness</small>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'ExecuteAttackView',
  
  setup() {
    const store = useStore()
    const toast = useToast()
    
    // State
    const loading = ref(true)
    const executing = ref(false)
    const attacks = ref([])
    const prompts = ref([])
    const selectedAttack = ref(null)
    const selectedPrompt = ref(null)
    const customPrompt = ref('')
    const jailbreakResult = ref(null)
    const modelResponse = ref('')
    const successRating = ref(5)
    const activeTabIndex = ref(0)
    
    // Tabs
    const tabs = [
      { header: 'Original Prompt' },
      { header: 'Jailbreak Prompt' },
      { header: 'Model Response' }
    ]
    
    // Prompt source options
    const promptSources = [
      { name: 'Existing Prompt', value: 'existing' },
      { name: 'Custom Prompt', value: 'custom' }
    ]
    const promptSource = ref(promptSources[0])
    
    // Computed properties
    const isFormValid = computed(() => {
      if (!selectedAttack.value) return false
      
      if (promptSource.value.value === 'existing') {
        return !!selectedPrompt.value
      } else {
        return !!customPrompt.value.trim()
      }
    })
    
    // Methods
    const fetchData = async () => {
      loading.value = true
      
      try {
        await Promise.all([
          store.dispatch('fetchAttacks'),
          store.dispatch('fetchPrompts')
        ])
        
        attacks.value = store.state.attacks
        prompts.value = store.state.prompts
        
        // 检查localStorage中是否存在selectedAttackId
        const selectedAttackId = localStorage.getItem('selectedAttackId')
        
        if (selectedAttackId && attacks.value.length > 0) {
          // 查找对应的攻击
          const foundAttack = attacks.value.find(attack => attack.id === parseInt(selectedAttackId))
          if (foundAttack) {
            selectedAttack.value = foundAttack
          } else {
            // 如果找不到对应的攻击，则使用默认值
            selectedAttack.value = attacks.value[0]
          }
          // 使用后清除localStorage中的值，避免影响下次访问
          localStorage.removeItem('selectedAttackId')
        } else if (attacks.value.length > 0) {
          // 如果没有selectedAttackId，则使用默认值
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
      }
    }
    
    const testWithLLM = async () => {
      if (!jailbreakResult.value) return
      
      executing.value = true
      modelResponse.value = ''
      
      try {
        // This would normally call an API to test with a real LLM
        // For now, we'll simulate a response
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        modelResponse.value = "This is a simulated response from the LLM. In a real implementation, this would be the actual response from the LLM API to the jailbreak prompt."
        activeTabIndex.value = 2
        
        toast.add({
          severity: 'info',
          summary: 'Response Received',
          detail: 'LLM response received',
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
    
    onMounted(() => {
      fetchData()
    })
    
    return {
      loading,
      executing,
      attacks,
      prompts,
      selectedAttack,
      selectedPrompt,
      customPrompt,
      promptSources,
      promptSource,
      jailbreakResult,
      modelResponse,
      successRating,
      isFormValid,
      executeAttack,
      testWithLLM,
      saveResult,
      tabs,
      activeTabIndex
    }
  }
}
</script>

<style scoped>
/* Custom styles specific to this component */
.prompt-display {
  white-space: pre-wrap;
  font-family: monospace;
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.jailbreak-prompt {
  background-color: #ffe8e8;
  border: 1px solid #ffcaca;
}

.model-response {
  background-color: #e8f4ff;
  border: 1px solid #c5e1ff;
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
</style>