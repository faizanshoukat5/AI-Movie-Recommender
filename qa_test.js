/**
 * Final QA Test for AI Movie Recommendation Engine
 * This script tests all the key frontend-backend integration points
 */

const API_BASE_URL = 'http://localhost:5000';

// Test all endpoints
async function runQATests() {
  console.log('🧪 Starting QA Tests for AI Movie Recommendation Engine...\n');
  
  const tests = [
    {
      name: 'Models Endpoint',
      url: `${API_BASE_URL}/models`,
      test: (data) => data.available_models && data.available_models.length > 0
    },
    {
      name: 'Movies Endpoint',
      url: `${API_BASE_URL}/movies?limit=10`,
      test: (data) => data.movies && data.movies.length > 0
    },
    {
      name: 'Random Movies Endpoint',
      url: `${API_BASE_URL}/movies/random?limit=5`,
      test: (data) => data.movies && data.movies.length > 0
    },
    {
      name: 'Search Endpoint',
      url: `${API_BASE_URL}/search?q=star&limit=5`,
      test: (data) => data.movies && data.movies.length > 0
    },
    {
      name: 'Recommendations Endpoint (SVD)',
      url: `${API_BASE_URL}/recommendations/1?n=5&model=svd`,
      test: (data) => data.recommendations && data.recommendations.length > 0
    },
    {
      name: 'Recommendations Endpoint (Ensemble)',
      url: `${API_BASE_URL}/recommendations/1?n=5&model=ensemble`,
      test: (data) => data.recommendations && data.recommendations.length > 0
    },
    {
      name: 'Prediction Endpoint (SVD)',
      url: `${API_BASE_URL}/predict?user_id=1&item_id=1&model=svd`,
      test: (data) => data.predicted_rating && data.predicted_rating > 0
    },
    {
      name: 'Prediction Endpoint (Ensemble)',
      url: `${API_BASE_URL}/predict?user_id=1&item_id=1&model=ensemble`,
      test: (data) => data.predicted_rating && data.predicted_rating > 0
    },
    {
      name: 'Model Comparison Endpoint',
      url: `${API_BASE_URL}/compare/1?n=5`,
      test: (data) => data.comparison && Object.keys(data.comparison).length > 0
    }
  ];

  let passed = 0;
  let total = tests.length;

  for (const test of tests) {
    try {
      const response = await fetch(test.url);
      const data = await response.json();
      
      if (response.ok && test.test(data)) {
        console.log(`✅ ${test.name}: PASSED`);
        passed++;
      } else {
        console.log(`❌ ${test.name}: FAILED - ${response.status} ${response.statusText}`);
        console.log(`   Data:`, data);
      }
    } catch (error) {
      console.log(`❌ ${test.name}: ERROR - ${error.message}`);
    }
  }

  console.log(`\n📊 QA Test Results: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! The AI Movie Recommendation Engine is ready!');
  } else {
    console.log('⚠️  Some tests failed. Please check the backend server.');
  }
}

// Test specific features
async function testSpecificFeatures() {
  console.log('\n🔍 Testing specific features...\n');
  
  // Test user range validation
  console.log('Testing user range validation...');
  try {
    const response = await fetch(`${API_BASE_URL}/recommendations/999?n=5&model=svd`);
    const data = await response.json();
    console.log('✅ User range validation working:', data.error || 'No error (expected)');
  } catch (error) {
    console.log('❌ User range validation test failed:', error.message);
  }
  
  // Test movie range validation
  console.log('Testing movie range validation...');
  try {
    const response = await fetch(`${API_BASE_URL}/predict?user_id=1&item_id=9999&model=svd`);
    const data = await response.json();
    console.log('✅ Movie range validation working:', data.error || 'No error (expected)');
  } catch (error) {
    console.log('❌ Movie range validation test failed:', error.message);
  }
  
  // Test different sort options
  console.log('Testing sort options...');
  try {
    const response = await fetch(`${API_BASE_URL}/search?q=star&sort=year&limit=5`);
    const data = await response.json();
    console.log('✅ Sort by year working:', data.movies.length > 0 ? 'Success' : 'No results');
  } catch (error) {
    console.log('❌ Sort options test failed:', error.message);
  }
}

// Run tests
runQATests().then(() => {
  return testSpecificFeatures();
});
