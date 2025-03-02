<template>
  <div class="attack-detail-view">
    <div v-if="loading" class="loading-container">
      <ProgressSpinner />
      <span class="ml-2">Loading attack details...</span>
    </div>
    
    <div v-else-if="!attack" class="error-container">
      <div class="error-message">
        <i class="pi pi-exclamation-triangle" style="font-size: 3rem"></i>
        <h2>Attack Not Found</h2>
        <p>The requested attack could not be found.</p>
        <Button label="Back to Attacks" icon="pi pi-arrow-left" @click="navigateToAttacks" />
      </div>
    </div>
    
    <div v-else>
      <div class="page-title">
        <div class="title-section">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="navigateToAttacks" />
          <h1>{{ attack.name }}</h1>
        </div>
        <div class="action-buttons">
          <Button label="Edit Attack" icon="pi pi-pencil" class="p-button-outlined p-mr-2" @click="editAttack" />
          <Button label="Execute Attack" icon="pi pi-bolt" @click="executeAttack" />
        </div>
      </div>
      
      <div class="grid">
        <div class="col-12 md:col-4">
          <Card>
            <template #title>
              <h2>Attack Information</h2>
            </template>
            <template #content>
              <div class="detail-item">
                <span class="detail-label">Name:</span>
                <span class="detail-value">{{ attack.name }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">Algorithm Type:</span>
                <span class="detail-value">
                  <Tag :value="attack.algorithm_type" severity="info" />
                </span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">Created:</span>
                <span class="detail-value">{{ formatDate(attack.created_at) }}</span>
              </div>
              
              <Divider />
              
              <div class="detail-item">
                <span class="detail-label">Description:</span>
              </div>
              <div class="description">
                {{ attack.description || 'No description provided.' }}
              </div>
              
              <Divider />
              
              <div v-if="attack.parameters">
                <div class="detail-item">
                  <span class="detail-label">Parameters:</span>
                </div>
                <div class="parameters">
                  <pre>{{ formatParameters(attack.parameters) }}</pre>
                </div>
              </div>
            </template>
          </Card>
          
          <Card class="mt-3">
            <template #title>
              <h2>Performance Summary</h2>
            </template>
            <template #content>
              <div v-if="attackStats">
                <div class="stats-grid">
                  <div class="stats-item">
                    <div class="stats-value">{{ attackStats.total_attempts || 0 }}</div>
                    <div class="stats-label">Total Tests</div>
                  </div>
                  
                  <div class="stats-item">
                    <div class="stats-value">{{ attackStats.successful_attempts || 0 }}</div>
                    <div class="stats-label">Successful</div>
                  </div>
                  
                  <div class="stats-item">
                    <div class="stats-value">{{ formatSuccessRate(attackStats) }}</div>
                    <div class="stats-label">Success Rate</div>
                  </div>
                  
                  <div class="stats-item">
                    <div class="stats-value">{{ formatRating(attackStats.avg_success_rating) }}</div>
                    <div class="stats-label">Avg. Rating</div>
                  </div>
                </div>
                
                <div class="mt-3">
                  <h3>Success Rate</h3>
                  <div class="success-rate-bar">
                    <div class="success-rate-fill" 
                         :style="{ width: calculateSuccessRate(attackStats) + '%' }">
                      {{ formatSuccessRate(attackStats) }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-stats">
                <p>No test results available for this attack yet.</p>
                <Button label="Execute Attack" icon="pi pi-bolt" @click="executeAttack" />
              </div>
            </template>
          </Card>
        </div>
        
        <div class="col-12 md:col-8">
          <Card>
            <template #title>
              <div class="flex align-items-center justify-content-between">
                <h2>Test Results</h2>
                <Button label="View All Results" icon="pi pi-list" class="p-button-text" @click="navigateToResults" />
              </div>
            </template>
            <template #content>
              <DataTable :value="results" :paginator="true" :rows="5" 
                         :loading="loadingResults" responsiveLayout="scroll"
                         :globalFilterFields="['original_prompt', 'jailbreak_prompt', 'model_response']">
                <template #empty>
                  <div class="p-text-center">No results found for this attack.</div>
                </template>
                <template #loading>
                  <div class="p-text-center">Loading results...</div>
                </template>
                
                <Column field="id" header="ID" sortable style="width: 5rem"></Column>
                <Column field="original_prompt" header="Original Prompt" sortable>
                  <template #body="slotProps">
                    <div class="truncated-text">{{ slotProps.data.original_prompt }}</div>
                  </template>
                </Column>
                <Column field="success_rating" header="Success" sortable style="width: 8rem">
                  <template #body="slotProps">
                    <div v-if="slotProps.data.success_rating !== null">
                      <Rating v-model="slotProps.data.success_rating" :readonly="true" :cancel="false" />
                      <span class="ml-2">{{ slotProps.data.success_rating }}/10</span>
                    </div>
                    <div v-else>Not rated</div>
                  </template>
                </Column>
                <Column field="created_at" header="Date" sortable style="width: 10rem">
                  <template #body="slotProps">
                    {{ formatDate(slotProps.data.created_at) }}
                  </template>
                </Column>
                <Column header="Actions" style="width: 8rem">
                  <template #body="slotProps">
                    <Button icon="pi pi-eye" class="p-button-rounded p-button-info" 
                            @click="viewResult(slotProps.data)" />
                  </template>
                </Column>
              </DataTable>
            </template>
          </Card>
          
          <Card class="mt-3">
            <template #title>
              <h2>Performance Over Time</h2>
            </template>
            <template #content>
              <div v-if="results.length > 0" class="chart-container">
                <Chart type="line" :data="lineChartData" :options="lineChartOptions" />
              </div>
              <div v-else class="empty-chart">
                <p>No data available to display chart.</p>
              </div>
            </template>
          </Card>
        </div>
      </div>
      
      <!-- Result Detail Dialog -->
      <Dialog v-model:visible="resultDetailDialog" :header="'Result Details #' + (selectedResult?.id || '')" 
              :style="{width: '80%', maxWidth: '1000px'}" :modal="true">
        <div v-if="selectedResult" class="result-detail">
          <TabView>
            <TabPanel header="Original Prompt">
              <div class="prompt-display">{{ selectedResult.original_prompt }}</div>
            </TabPanel>
            
            <TabPanel header="Jailbreak Prompt">
              <div class="prompt-display jailbreak-prompt">{{ selectedResult.jailbreak_prompt }}</div>
            </TabPanel>
            
            <TabPanel header="Model Response" v-if="selectedResult.model_response">
              <div class="prompt-display model-response">{{ selectedResult.model_response }}</div>
            </TabPanel>
          </TabView>
          
          <Divider />
          
          <div class="detail-item">
            <span class="detail-label">Success Rating:</span>
            <span class="detail-value">
              <Rating v-model="selectedResult.success_rating" :readonly="true" :cancel="false" />
              {{ selectedResult.success_rating }}/10
            </span>
          </div>
          
          <div class="detail-item">
            <span class="detail-label">Date:</span>
            <span class="detail-value">{{ formatDate(selectedResult.created_at) }}</span>
          </div>
        </div>
      </Dialog>
      
      <!-- Edit Attack Dialog -->
      <Dialog v-model:visible="editDialog" header="Edit Attack" :style="{width: '500px'}" 
              :modal="true" class="p-fluid">
        <div class="p-field">
          <label for="name">Name</label>
          <InputText id="name" v-model="editedAttack.name" required />
        </div>
        
        <div class="p-field">
          <label for="algorithm_type">Algorithm Type</label>
          <Dropdown id="algorithm_type" v-model="editedAttack.algorithm_type" 
                    :options="algorithmTypes" placeholder="Select Algorithm Type" />
        </div>
        
        <div class="p-field">
          <label for="description">Description</label>
          <Textarea id="description" v-model="editedAttack.description" rows="5" />
        </div>
        
        <div class="p-field">
          <label for="parameters">Parameters (JSON)</label>
          <Textarea id="parameters" v-model="editedAttack.parametersJson" rows="5" />
          <small v-if="parametersError" class="p-error">{{ parametersError }}</small>
        </div>
        
        <template #footer>
          <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="cancelEdit" />
          <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveAttack" />
        </template>
      </Dialog>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';
import { useToast } from 'primevue/usetoast';

export default {
  name: 'AttackDetailView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  
  setup(props) {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    const toast = useToast();
    
    // Data
    const attack = ref(null);
    const results = ref([]);
    const attackStats = ref(null);
    const loading = ref(true);
    const loadingResults = ref(true);
    const selectedResult = ref(null);
    const resultDetailDialog = ref(false);
    const editDialog = ref(false);
    const editedAttack = ref({});
    const parametersError = ref('');
    
    // Algorithm types
    const algorithmTypes = [
      'template_based',
      'character_stuffing',
      'multi_language',
      'token_limit',
      'json_injection'
    ];
    
    // Methods
    const fetchAttack = async () => {
      loading.value = true;
      try {
        const attackData = await store.dispatch('fetchAttack', props.id);
        attack.value = attackData;
      } catch (error) {
        console.error('Error fetching attack:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load attack details',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const fetchResults = async () => {
      loadingResults.value = true;
      try {
        await store.dispatch('fetchResults', props.id);
        results.value = store.state.results;
        
        // Extract stats from results
        if (results.value.length > 0) {
          const totalAttempts = results.value.length;
          const successfulAttempts = results.value.filter(r => r.success_rating > 7).length;
          const avgRating = results.value.reduce((sum, r) => sum + (r.success_rating || 0), 0) / totalAttempts;
          
          attackStats.value = {
            total_attempts: totalAttempts,
            successful_attempts: successfulAttempts,
            avg_success_rating: avgRating
          };
        }
      } catch (error) {
        console.error('Error fetching results:', error);
      } finally {
        loadingResults.value = false;
      }
    };
    
    const navigateToAttacks = () => {
      router.push('/attacks');
    };
    
    const navigateToResults = () => {
      router.push('/results');
    };
    
    const executeAttack = () => {
      router.push({
        path: '/execute-attack',
        query: { attack: props.id }
      });
    };
    
    const viewResult = (result) => {
      selectedResult.value = result;
      resultDetailDialog.value = true;
    };
    
    const editAttack = () => {
      editedAttack.value = { ...attack.value };
      
      // Convert parameters to JSON string for editing
      if (editedAttack.value.parameters) {
        try {
          const params = typeof editedAttack.value.parameters === 'string' 
            ? JSON.parse(editedAttack.value.parameters) 
            : editedAttack.value.parameters;
          
          editedAttack.value.parametersJson = JSON.stringify(params, null, 2);
        } catch (e) {
          editedAttack.value.parametersJson = editedAttack.value.parameters;
        }
      } else {
        editedAttack.value.parametersJson = '';
      }
      
      parametersError.value = '';
      editDialog.value = true;
    };
    
    const cancelEdit = () => {
      editDialog.value = false;
    };
    
    const saveAttack = async () => {
      // Validate parameters JSON
      if (editedAttack.value.parametersJson) {
        try {
          JSON.parse(editedAttack.value.parametersJson);
          parametersError.value = '';
        } catch (e) {
          parametersError.value = 'Invalid JSON format';
          return;
        }
      }
      
      try {
        const updatedAttack = {
          name: editedAttack.value.name,
          description: editedAttack.value.description,
          algorithm_type: editedAttack.value.algorithm_type,
          parameters: editedAttack.value.parametersJson ? JSON.parse(editedAttack.value.parametersJson) : null
        };
        
        await store.dispatch('updateAttack', {
          attackId: props.id,
          attackData: updatedAttack
        });
        
        // Refresh attack data
        await fetchAttack();
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attack updated successfully',
          life: 3000
        });
        
        editDialog.value = false;
      } catch (error) {
        console.error('Error updating attack:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to update attack',
          life: 3000
        });
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date);
    };
    
    const formatParameters = (parameters) => {
      if (!parameters) return '';
      
      try {
        const params = typeof parameters === 'string' ? JSON.parse(parameters) : parameters;
        return JSON.stringify(params, null, 2);
      } catch (e) {
        return parameters;
      }
    };
    
    const formatRating = (value) => {
      return value ? value.toFixed(1) : 'N/A';
    };
    
    const calculateSuccessRate = (stats) => {
      if (!stats || !stats.total_attempts) return 0;
      return (stats.successful_attempts / stats.total_attempts) * 100;
    };
    
    const formatSuccessRate = (stats) => {
      return calculateSuccessRate(stats).toFixed(1) + '%';
    };
    
    // Chart data
    const lineChartData = computed(() => {
      if (results.value.length === 0) return { labels: [], datasets: [] };
      
      // Sort results by date
      const sortedResults = [...results.value].sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
      );
      
      // Extract dates and ratings
      const labels = sortedResults.map(r => formatDate(r.created_at));
      const ratings = sortedResults.map(r => r.success_rating || 0);
      
      // Calculate moving average if enough data points
      const movingAverages = [];
      const windowSize = 3;
      
      if (ratings.length >= windowSize) {
        for (let i = 0; i < ratings.length - windowSize + 1; i++) {
          const windowSum = ratings.slice(i, i + windowSize).reduce((sum, val) => sum + val, 0);
          movingAverages.push(windowSum / windowSize);
        }
        
        // Pad the beginning of the moving average array
        for (let i = 0; i < windowSize - 1; i++) {
          movingAverages.unshift(null);
        }
      }
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Success Rating',
            data: ratings,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            tension: 0.4
          },
          ...(movingAverages.length > 0 ? [{
            label: 'Moving Average',
            data: movingAverages,
            borderColor: '#10b981',
            borderDash: [5, 5],
            fill: false,
            tension: 0.4
          }] : [])
        ]
      };
    });
    
    const lineChartOptions = {
      scales: {
        y: {
          beginAtZero: true,
          max: 10,
          title: {
            display: true,
            text: 'Success Rating'
          }
        }
      },
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    };
    
    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([fetchAttack(), fetchResults()]);
    });
    
    return {
      attack,
      results,
      attackStats,
      loading,
      loadingResults,
      selectedResult,
      resultDetailDialog,
      editDialog,
      editedAttack,
      parametersError,
      algorithmTypes,
      navigateToAttacks,
      navigateToResults,
      executeAttack,
      viewResult,
      editAttack,
      cancelEdit,
      saveAttack,
      formatDate,
      formatParameters,
      formatRating,
      calculateSuccessRate,
      formatSuccessRate,
      lineChartData,
      lineChartOptions
    };
  }
}
</script>

<style scoped>
.attack-detail-view {
  padding: 1rem;
}

.loading-container, .error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.error-message {
  text-align: center;
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.title-section {
  display: flex;
  align-items: center;
}

.title-section h1 {
  margin: 0 0 0 0.5rem;
}

.detail-item {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}

.detail-label {
  font-weight: bold;
  margin-right: 0.5rem;
  min-width: 100px;
}

.description, .parameters {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.parameters pre {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 4px;
  overflow: auto;
  font-size: 0.875rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stats-item {
  text-align: center;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stats-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.success-rate-bar {
  background-color: #e5e7eb;
  border-radius: 4px;
  height: 20px;
  width: 100%;
  overflow: hidden;
}

.success-rate-fill {
  background-color: #4f46e5;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  min-width: 30px;
}

.truncated-text {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-container {
  height: 300px;
  position: relative;
}

.empty-stats, .empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.mt-3 {
  margin-top: 1rem;
}

.prompt-display {
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 1rem;
  white-space: pre-wrap;
  font-family: monospace;
}

.jailbreak-prompt {
  background-color: #ffe8e8;
  border: 1px solid #ffcaca;
}

.model-response {
  background-color: #e8f4ff;
  border: 1px solid #c5e1ff;
}
</style> 