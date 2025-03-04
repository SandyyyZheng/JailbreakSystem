<template>
  <div class="home">
    <div class="page-title">
      <h1>Jailbreak System for Large Language Models</h1>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <div class="stats-card">
          <div class="stats-value">{{ attackCount }}</div>
          <div class="stats-label">Jailbreak Attacks</div>
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="stats-card">
          <div class="stats-value">{{ promptCount }}</div>
          <div class="stats-label">Test Prompts</div>
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="stats-card">
          <div class="stats-value">{{ resultCount }}</div>
          <div class="stats-label">Test Results</div>
        </div>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <div class="stats-card">
          <div class="stats-value">{{ successRate }}%</div>
          <div class="stats-label">Success Rate</div>
        </div>
      </div>
    </div>
    
    <div class="grid mt-4">
      <div class="col-12 md:col-6">
        <Card>
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <h3>Quick Actions</h3>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6 mb-3">
                <Button label="Execute Attack" icon="pi pi-bolt" class="p-button-primary w-full" @click="navigateToExecuteAttack" />
              </div>
              <div class="col-12 md:col-6 mb-3">
                <Button label="Create Attack" icon="pi pi-plus" class="p-button-secondary w-full" @click="navigateToAttacks" />
              </div>
              <div class="col-12 md:col-6 mb-3">
                <Button label="Add Prompt" icon="pi pi-pencil" class="p-button-secondary w-full" @click="navigateToPrompts" />
              </div>
              <div class="col-12 md:col-6 mb-3">
                <Button label="View Results" icon="pi pi-chart-bar" class="p-button-secondary w-full" @click="navigateToResults" />
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6">
        <Card>
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <h3>Recent Results</h3>
              <Button label="View All" icon="pi pi-arrow-right" class="p-button-text" @click="navigateToResults" />
            </div>
          </template>
          <template #content>
            <div v-if="loading" class="loading-container">
              <ProgressSpinner />
            </div>
            <div v-else-if="recentResults.length === 0" class="text-center p-4">
              <p>No results yet. Try executing an attack!</p>
            </div>
            <div v-else>
              <DataTable :value="recentResults" responsiveLayout="scroll" class="p-datatable-sm">
                <Column field="attack_name" header="Attack"></Column>
                <Column field="success_rating" header="Harmful Score">
                  <template #body="slotProps">
                    <div v-if="slotProps.data.success_rating">
                      {{ slotProps.data.success_rating }}/5
                    </div>
                    <div v-else>
                      N/A
                    </div>
                  </template>
                </Column>
                <Column header="Actions">
                  <template #body="slotProps">
                    <Button icon="pi pi-eye" class="p-button-text p-button-sm" @click="viewResult(slotProps.data.id)" />
                  </template>
                </Column>
              </DataTable>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'HomeView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const loading = ref(true)
    const recentResults = ref([])
    
    // Stats
    const attackCount = computed(() => store.state.attacks.length)
    const promptCount = computed(() => store.state.prompts.length)
    const resultCount = computed(() => store.state.results.length)
    const successRate = computed(() => {
      if (store.state.results.length === 0) return 0
      
      const successfulResults = store.state.results.filter(result => result.success_rating > 3).length
      return Math.round((successfulResults / store.state.results.length) * 100)
    })
    
    // Navigation methods
    const navigateToExecuteAttack = () => {
      router.push('/execute-attack')
    }
    
    const navigateToAttacks = () => {
      router.push('/attacks')
    }
    
    const navigateToPrompts = () => {
      router.push('/prompts')
    }
    
    const navigateToResults = () => {
      router.push('/results')
    }
    
    const viewResult = (resultId) => {
      router.push(`/results?id=${resultId}`)
    }
    
    // Fetch data
    const fetchData = async () => {
      loading.value = true
      
      try {
        await Promise.all([
          store.dispatch('fetchAttacks'),
          store.dispatch('fetchPrompts'),
          store.dispatch('fetchResults')
        ])
        
        // Get recent results (last 5)
        recentResults.value = [...store.state.results]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 5)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      fetchData()
    })
    
    return {
      loading,
      recentResults,
      attackCount,
      promptCount,
      resultCount,
      successRate,
      navigateToExecuteAttack,
      navigateToAttacks,
      navigateToPrompts,
      navigateToResults,
      viewResult
    }
  }
}
</script> 