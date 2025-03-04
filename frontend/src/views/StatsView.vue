<template>
  <div class="stats-view">
    <div class="page-title">
      <h1>Jailbreak Statistics</h1>
    </div>
    
    <div v-if="loading" class="loading-container">
      <ProgressSpinner />
      <span class="ml-2">Loading statistics...</span>
    </div>
    
    <div v-else-if="stats && Object.keys(stats).length > 0">
      <!-- Summary Stats -->
      <div class="grid">
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon">
              <i class="pi pi-bolt"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ stats.total_results || 0 }}</div>
              <div class="stats-label">Total Tests</div>
            </div>
          </div>
        </div>
        
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon success">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ stats.harmful_results || 0 }}</div>
              <div class="stats-label">Successful Jailbreaks</div>
            </div>
          </div>
        </div>
        
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon info">
              <i class="pi pi-percentage"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ formatPercentage(stats.harmful_rate || 0) }}</div>
              <div class="stats-label">Attack Success Rate</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Attack Stats -->
      <div class="card mt-4">
        <h2>Attack Performance</h2>
        <div class="grid">
          <div class="col-12 md:col-6">
            <DataTable :value="stats.attack_stats || []" 
                      responsiveLayout="scroll" 
                      class="p-datatable-sm"
                      :scrollable="true"
                      scrollHeight="300px"
                      :rows="5"
                      :rowsPerPageOptions="[5, 10, 20]">
              <Column field="name" header="Attack Name"></Column>
              <Column field="algorithm_type" header="Type"></Column>
              <Column field="total_attempts" header="Tests"></Column>
              <Column field="avg_harmful_score" header="Avg. Harmful">
                <template #body="slotProps">
                  {{ formatRating(slotProps.data.avg_harmful_score) }}
                </template>
              </Column>
              <Column header="Attack Success Rate">
                <template #body="slotProps">
                  <div class="success-rate-bar">
                    <div class="success-rate-fill" 
                         :style="{ width: calculateAttackSuccessRate(slotProps.data) + '%' }">
                      {{ formatPercentage(calculateAttackSuccessRate(slotProps.data) / 100) }}
                    </div>
                  </div>
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="chart-container bar-chart-container">
              <h3 class="chart-title">Attack Success Rate by Attack</h3>
              <Chart type="bar" :data="barChartData" :options="barChartOptions" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Algorithm Type Comparison -->
      <div class="card mt-4">
        <h2 class="chart-title text-left">Algorithm Type Comparison</h2>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="chart-container pie-chart-container bg-light-gray">
              <h3 class="chart-title text-center">Tests by Algorithm Type</h3>
              <Chart type="pie" :data="pieChartData" :options="pieChartOptions" />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="chart-container radar-chart-container bg-light-gray">
              <h3 class="chart-title text-center">Average Harmful Score by Algorithm Type</h3>
              <Chart type="radar" :data="radarChartData" :options="radarChartOptions" />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="card p-4 text-center">
      <h3>No statistics available</h3>
      <p>Try executing some jailbreak attacks to generate statistics.</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'StatsView',
  
  setup() {
    const store = useStore();
    
    // Data
    const stats = ref({});
    const loading = ref(true);
    
    // Methods
    const fetchStats = async () => {
      loading.value = true;
      try {
        const response = await store.dispatch('fetchStats');
        if (response) {
          stats.value = response;
        } else {
          stats.value = {
            total_results: 0,
            harmful_results: 0,
            harmful_rate: 0,
            attack_stats: []
          };
        }
      } catch (error) {
        console.error('Error fetching statistics:', error);
        stats.value = {
          total_results: 0,
          harmful_results: 0,
          harmful_rate: 0,
          attack_stats: []
        };
      } finally {
        loading.value = false;
      }
    };
    
    const formatPercentage = (value) => {
      return (value * 100).toFixed(1) + '%';
    };
    
    const formatRating = (value) => {
      return value ? value.toFixed(1) : 'N/A';
    };
    
    const calculateAttackSuccessRate = (attack) => {
      if (!attack || !attack.total_attempts) return 0;
      return (attack.harmful_attempts / attack.total_attempts) * 100;
    };
    
    // Chart data
    const barChartData = computed(() => {
      if (!stats.value || !stats.value.attack_stats) {
        return { labels: [], datasets: [{ label: 'Attack Success Rate (%)', backgroundColor: '#4f46e5', data: [] }] };
      }
      
      const labels = stats.value.attack_stats.map(attack => attack.name);
      const harmfulRates = stats.value.attack_stats.map(attack => 
        calculateAttackSuccessRate(attack)
      );
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Attack Success Rate (%)',
            backgroundColor: '#4f46e5',
            data: harmfulRates
          }
        ]
      };
    });
    
    const barChartOptions = {
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Attack Success Rate (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.raw.toFixed(1) + '%';
            }
          }
        }
      }
    };
    
    const pieChartData = computed(() => {
      if (!stats.value || !stats.value.attack_stats) {
        return { 
          labels: [], 
          datasets: [{ 
            data: [], 
            backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'] 
          }] 
        };
      }
      
      // Group attacks by algorithm type
      const algorithmTypes = {};
      stats.value.attack_stats.forEach(attack => {
        if (!algorithmTypes[attack.algorithm_type]) {
          algorithmTypes[attack.algorithm_type] = 0;
        }
        algorithmTypes[attack.algorithm_type] += attack.total_attempts || 0;
      });
      
      const labels = Object.keys(algorithmTypes);
      const data = Object.values(algorithmTypes);
      
      return {
        labels: labels,
        datasets: [
          {
            data: data,
            backgroundColor: [
              '#4f46e5',
              '#10b981',
              '#f59e0b',
              '#ef4444',
              '#8b5cf6'
            ]
          }
        ]
      };
    });
    
    const pieChartOptions = {
      plugins: {
        legend: {
          position: 'bottom'
        },
        title: {
          display: false,
          text: 'Tests by Algorithm Type'
        }
      }
    };
    
    const radarChartData = computed(() => {
      if (!stats.value || !stats.value.attack_stats) {
        return { 
          labels: [], 
          datasets: [{ 
            label: 'Avg. Harmful Score',
            data: [],
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            borderColor: '#4f46e5',
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#4f46e5'
          }] 
        };
      }
      
      // Group attacks by algorithm type and calculate average success rating
      const algorithmTypes = {};
      stats.value.attack_stats.forEach(attack => {
        if (!algorithmTypes[attack.algorithm_type]) {
          algorithmTypes[attack.algorithm_type] = {
            total: 0,
            count: 0,
            avg: 0
          };
        }
        
        if (attack.avg_harmful_score) {
          algorithmTypes[attack.algorithm_type].total += attack.avg_harmful_score;
          algorithmTypes[attack.algorithm_type].count += 1;
        }
      });
      
      // Calculate averages
      Object.keys(algorithmTypes).forEach(type => {
        const typeStats = algorithmTypes[type];
        if (typeStats.count > 0) {
          typeStats.avg = typeStats.total / typeStats.count;
        }
      });
      
      const labels = Object.keys(algorithmTypes);
      const data = labels.map(label => algorithmTypes[label].avg);
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Avg. Harmful Score',
            data: data,
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            borderColor: '#4f46e5',
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#4f46e5'
          }
        ]
      };
    });
    
    const radarChartOptions = {
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: 5
        }
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchStats();
    });
    
    return {
      stats,
      loading,
      formatPercentage,
      formatRating,
      calculateAttackSuccessRate,
      barChartData,
      barChartOptions,
      pieChartData,
      pieChartOptions,
      radarChartData,
      radarChartOptions
    };
  }
}
</script>

<style scoped>
.stats-view {
  padding: 1rem;
}

.page-title {
  margin-bottom: 1.5rem;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.stats-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.stats-icon i {
  font-size: 1.5rem;
}

.stats-icon.success {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stats-icon.info {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stats-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.card h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.25rem;
  text-align: center;
}

.mt-4 {
  margin-top: 1.5rem;
}

.chart-container {
  position: relative;
}

.bar-chart-container {
  height: 300px;
  width: 100%;
}

.pie-chart-container {
  height: 550px;
  width: 85%;
}

.radar-chart-container {
  height: 550px;
  width: 100%;
}

.chart-title {
  font-size: 1.25rem;
  text-align: center;
}

.bg-light-gray {
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 5px;
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
</style> 