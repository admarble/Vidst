import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EnhancedComponentEvaluationMatrix = () => {
  // State for sorting
  const [sortConfig, setSortConfig] = useState({
    key: 'totalScore',
    direction: 'desc'
  });
  
  // State for filtering
  const [filterConfig, setFilterConfig] = useState({
    recommendation: 'all',
    minScore: 0,
    showHighPriorityOnly: false
  });
  
  // State for view mode
  const [viewMode, setViewMode] = useState('table'); // 'table', 'chart', 'combined'

  const components = [
    {
      id: 1,
      component: "Scene Detection",
      currentImplementation: "Custom OpenCV-based implementation",
      apiAlternative: "Twelve Labs Marengo/Pegasus",
      pocImportance: 5,
      implementationStatus: 3,
      complexityBurden: 4,
      apiViability: 5,
      accuracyRequirements: 4,
      costImpact: 4,
      integrationEffort: 4,
      recommendation: "Replace",
      timeline: "1 week",
      notes: "Twelve Labs significantly exceeds accuracy targets (94.2% vs 90% requirement) while reducing implementation complexity."
    },
    {
      id: 2,
      component: "Vector Storage",
      currentImplementation: "Self-hosted FAISS",
      apiAlternative: "Pinecone API",
      pocImportance: 5,
      implementationStatus: 4,
      complexityBurden: 5,
      apiViability: 5,
      accuracyRequirements: 3,
      costImpact: 5,
      integrationEffort: 4,
      recommendation: "Replace",
      timeline: "1-2 weeks",
      notes: "Eliminates infrastructure management while improving capabilities. Free tier available for POC."
    },
    {
      id: 3,
      component: "OCR (Text Extraction)",
      currentImplementation: "pytesseract/easyocr",
      apiAlternative: "Google Document AI",
      pocImportance: 4,
      implementationStatus: 2,
      complexityBurden: 4,
      apiViability: 5,
      accuracyRequirements: 5,
      costImpact: 3,
      integrationEffort: 4,
      recommendation: "Replace",
      timeline: "1 week",
      notes: "Current implementation doesn't meet 95% accuracy target. Document AI likely exceeds target with simpler implementation."
    },
    {
      id: 4,
      component: "Object Detection",
      currentImplementation: "YOLOv8 via ultralytics",
      apiAlternative: "Amazon Rekognition",
      pocImportance: 3,
      implementationStatus: 4,
      complexityBurden: 3,
      apiViability: 4,
      accuracyRequirements: 3,
      costImpact: 3,
      integrationEffort: 3,
      recommendation: "Phase Later",
      timeline: "2 weeks",
      notes: "Current implementation works well, but requires custom infrastructure. Consider API replacement in later phase."
    },
    {
      id: 5,
      component: "Audio Transcription",
      currentImplementation: "Whisper (placeholder)",
      apiAlternative: "Hybrid (Whisper + Twelve Labs)",
      pocImportance: 5,
      implementationStatus: 1,
      complexityBurden: 4,
      apiViability: 4,
      accuracyRequirements: 5,
      costImpact: 3,
      integrationEffort: 3,
      recommendation: "Complete Current + API",
      timeline: "1-2 weeks",
      notes: "Complete Whisper implementation but add Twelve Labs as fallback. Required to meet 95% accuracy target."
    },
    {
      id: 6,
      component: "Natural Language Querying",
      currentImplementation: "Backend exists, interface missing",
      apiAlternative: "Twelve Labs Semantic Search",
      pocImportance: 5,
      implementationStatus: 2,
      complexityBurden: 4,
      apiViability: 5,
      accuracyRequirements: 4,
      costImpact: 4,
      integrationEffort: 4,
      recommendation: "Replace",
      timeline: "1 week",
      notes: "Twelve Labs exceeds relevance target (92.3% vs 85% requirement) with significantly simpler implementation."
    },
    {
      id: 7,
      component: "File Storage",
      currentImplementation: "Local file management",
      apiAlternative: "AWS S3 + Lambda",
      pocImportance: 3,
      implementationStatus: 4,
      complexityBurden: 3,
      apiViability: 5,
      accuracyRequirements: 2,
      costImpact: 3,
      integrationEffort: 3,
      recommendation: "Phase Later",
      timeline: "1-2 weeks",
      notes: "Current implementation is sufficient for POC. Consider for later phases or if scalability becomes important."
    },
    {
      id: 8,
      component: "Caching",
      currentImplementation: "Redis-based caching",
      apiAlternative: "Momento Cache",
      pocImportance: 2,
      implementationStatus: 3,
      complexityBurden: 2,
      apiViability: 4,
      accuracyRequirements: 2,
      costImpact: 4,
      integrationEffort: 4,
      recommendation: "Keep Current",
      timeline: "1 week",
      notes: "Redis is relatively simple to implement. Low priority for replacement unless infrastructure simplification is critical."
    },
    {
      id: 9,
      component: "Video Processing",
      currentImplementation: "Custom processing pipeline with ffmpeg",
      apiAlternative: "AWS Elemental MediaConvert",
      pocImportance: 4,
      implementationStatus: 4,
      complexityBurden: 3,
      apiViability: 3,
      accuracyRequirements: 3, 
      costImpact: 2,
      integrationEffort: 2,
      recommendation: "Keep Current",
      timeline: "2 weeks",
      notes: "Current implementation works well. API replacement would require significant rework for minimal benefit in POC stage."
    },
    {
      id: 10,
      component: "Documentation",
      currentImplementation: "Dual systems (Sphinx + MkDocs)",
      apiAlternative: "N/A",
      pocImportance: 2,
      implementationStatus: 3,
      complexityBurden: 4,
      apiViability: 1,
      accuracyRequirements: 1,
      costImpact: 5,
      integrationEffort: 5,
      recommendation: "Consolidate",
      timeline: "2-3 days",
      notes: "Not an API issue, but significant complexity reduction by consolidating to a single documentation system."
    }
  ];

  // Add calculated total score
  const componentsWithScore = components.map(component => {
    const totalScore = (
      component.pocImportance * 3 + // Weight POC importance more heavily
      (5 - component.implementationStatus) * 2 + // Lower implementation status means more need for change
      component.complexityBurden * 2 +
      component.apiViability * 2 +
      component.accuracyRequirements +
      component.costImpact +
      component.integrationEffort
    );
    
    // Add priority categorization
    let priority;
    if (totalScore >= 45) {
      priority = "High";
    } else if (totalScore >= 35) {
      priority = "Medium";
    } else {
      priority = "Low";
    }
    
    return { ...component, totalScore, priority };
  });

  // Filter components based on filterConfig
  const filteredComponents = componentsWithScore.filter(component => {
    if (filterConfig.recommendation !== 'all' && component.recommendation !== filterConfig.recommendation) {
      return false;
    }
    
    if (component.totalScore < filterConfig.minScore) {
      return false;
    }
    
    if (filterConfig.showHighPriorityOnly && component.priority !== 'High') {
      return false;
    }
    
    return true;
  });

  // Sort components based on config
  const sortedComponents = [...filteredComponents].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  // Prepare data for charts
  const chartData = sortedComponents.map(item => ({
    name: item.component,
    score: item.totalScore,
    pocImportance: item.pocImportance * 3, // Weighted for visualization
    complexity: item.complexityBurden * 2, // Weighted for visualization
    apiViability: item.apiViability * 2, // Weighted for visualization
    implementation: (5 - item.implementationStatus) * 2, // Inverted and weighted
    recommendation: item.recommendation,
  }));

  // Handler for sort request
  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Get arrow direction for currently sorted column
  const getSortDirection = (name) => {
    if (sortConfig.key === name) {
      return sortConfig.direction === 'asc' ? '↑' : '↓';
    }
    return '';
  };
  
  // Get recommendation color
  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'Replace':
        return 'bg-red-100 text-red-800';
      case 'Complete Current + API':
        return 'bg-yellow-100 text-yellow-800';
      case 'Phase Later':
        return 'bg-blue-100 text-blue-800';
      case 'Keep Current':
        return 'bg-green-100 text-green-800';
      case 'Consolidate':
        return 'bg-purple-100 text-purple-800';
      default:
        return '';
    }
  };
  
  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High':
        return 'bg-red-50 text-red-700 font-bold';
      case 'Medium':
        return 'bg-yellow-50 text-yellow-700';
      case 'Low':
        return 'bg-green-50 text-green-700';
      default:
        return '';
    }
  };

  // Toggle view mode
  const toggleViewMode = (mode) => {
    setViewMode(mode);
  };
  
  // Update filter config
  const updateFilterConfig = (key, value) => {
    setFilterConfig({
      ...filterConfig,
      [key]: value
    });
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Component Evaluation Matrix</h2>
        
        {/* View Mode Selector */}
        <div className="flex mb-4 space-x-4">
          <button 
            onClick={() => toggleViewMode('table')}
            className={`px-4 py-2 rounded ${viewMode === 'table' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            Table View
          </button>
          <button 
            onClick={() => toggleViewMode('chart')}
            className={`px-4 py-2 rounded ${viewMode === 'chart' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            Chart View
          </button>
          <button 
            onClick={() => toggleViewMode('combined')}
            className={`px-4 py-2 rounded ${viewMode === 'combined' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            Combined View
          </button>
        </div>
        
        {/* Filters */}
        <div className="flex flex-wrap gap-4 p-4 bg-gray-50 rounded-lg mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recommendation</label>
            <select 
              value={filterConfig.recommendation}
              onChange={(e) => updateFilterConfig('recommendation', e.target.value)}
              className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="all">All</option>
              <option value="Replace">Replace</option>
              <option value="Complete Current + API">Complete Current + API</option>
              <option value="Phase Later">Phase Later</option>
              <option value="Keep Current">Keep Current</option>
              <option value="Consolidate">Consolidate</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Score</label>
            <input 
              type="number" 
              value={filterConfig.minScore}
              onChange={(e) => updateFilterConfig('minScore', parseInt(e.target.value) || 0)}
              className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
          
          <div className="flex items-end">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={filterConfig.showHighPriorityOnly}
                onChange={(e) => updateFilterConfig('showHighPriorityOnly', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">High Priority Only</span>
            </label>
          </div>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-700">Total Components</h3>
            <p className="text-2xl font-bold">{sortedComponents.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="font-semibold text-red-700">Replace Components</h3>
            <p className="text-2xl font-bold">
              {sortedComponents.filter(item => item.recommendation === 'Replace').length}
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="font-semibold text-yellow-700">High Priority</h3>
            <p className="text-2xl font-bold">
              {sortedComponents.filter(item => item.priority === 'High').length}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-700">Avg. Score</h3>
            <p className="text-2xl font-bold">
              {sortedComponents.length > 0 
                ? Math.round(sortedComponents.reduce((sum, item) => sum + item.totalScore, 0) / sortedComponents.length) 
                : 0
              }
            </p>
          </div>
        </div>
      </div>
      
      {/* Table View */}
      {(viewMode === 'table' || viewMode === 'combined') && (
        <div className="overflow-x-auto mb-8">
          <table className="min-w-full bg-white border border-gray-200">
            <thead className="bg-gray-100">
              <tr>
                <th 
                  className="px-4 py-2 text-left cursor-pointer"
                  onClick={() => requestSort('component')}
                >
                  Component {getSortDirection('component')}
                </th>
                <th 
                  className="px-4 py-2 text-left hidden md:table-cell"
                >
                  Current Implementation
                </th>
                <th 
                  className="px-4 py-2 text-left hidden lg:table-cell"
                >
                  API Alternative
                </th>
                <th 
                  className="px-4 py-2 text-center cursor-pointer"
                  onClick={() => requestSort('totalScore')}
                >
                  Score {getSortDirection('totalScore')}
                </th>
                <th 
                  className="px-4 py-2 text-center cursor-pointer"
                  onClick={() => requestSort('priority')}
                >
                  Priority {getSortDirection('priority')}
                </th>
                <th 
                  className="px-4 py-2 text-center cursor-pointer"
                  onClick={() => requestSort('recommendation')}
                >
                  Recommendation {getSortDirection('recommendation')}
                </th>
                <th 
                  className="px-4 py-2 text-center hidden sm:table-cell"
                >
                  Timeline
                </th>
                <th 
                  className="px-4 py-2 text-left hidden xl:table-cell"
                >
                  Notes
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedComponents.map((component) => (
                <tr key={component.id} className="border-t border-gray-200 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{component.component}</td>
                  <td className="px-4 py-3 text-sm hidden md:table-cell">{component.currentImplementation}</td>
                  <td className="px-4 py-3 text-sm hidden lg:table-cell">{component.apiAlternative}</td>
                  <td className="px-4 py-3 text-center font-bold">{component.totalScore}</td>
                  <td className={`px-4 py-3 text-center ${getPriorityColor(component.priority)}`}>{component.priority}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getRecommendationColor(component.recommendation)}`}>
                      {component.recommendation}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-sm hidden sm:table-cell">{component.timeline}</td>
                  <td className="px-4 py-3 text-sm hidden xl:table-cell">{component.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Chart View */}
      {(viewMode === 'chart' || viewMode === 'combined') && (
        <div className="mb-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Component Score Distribution</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={chartData}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 70,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={70} />
                <YAxis />
                <Tooltip formatter={(value, name) => {
                  if (name === 'score') return [`${value} points`, 'Total Score'];
                  if (name === 'pocImportance') return [`${value / 3} × 3`, 'POC Importance'];
                  if (name === 'complexity') return [`${value / 2} × 2`, 'Complexity Burden'];
                  if (name === 'apiViability') return [`${value / 2} × 2`, 'API Viability'];
                  if (name === 'implementation') return [`${(10 - value) / 2} × 2`, 'Implementation Status'];
                  return [value, name];
                }} />
                <Legend />
                <Bar dataKey="score" fill="#8884d8" name="Total Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Score Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 70,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={70} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="pocImportance" stackId="a" fill="#8884d8" name="POC Importance" />
                  <Bar dataKey="complexity" stackId="a" fill="#82ca9d" name="Complexity" />
                  <Bar dataKey="apiViability" stackId="a" fill="#ffc658" name="API Viability" />
                  <Bar dataKey="implementation" stackId="a" fill="#ff8042" name="Implementation Status" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Recommendations Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[
                    { name: 'Replace', count: sortedComponents.filter(c => c.recommendation === 'Replace').length, color: '#f87171' },
                    { name: 'Complete Current + API', count: sortedComponents.filter(c => c.recommendation === 'Complete Current + API').length, color: '#fbbf24' },
                    { name: 'Phase Later', count: sortedComponents.filter(c => c.recommendation === 'Phase Later').length, color: '#60a5fa' },
                    { name: 'Keep Current', count: sortedComponents.filter(c => c.recommendation === 'Keep Current').length, color: '#34d399' },
                    { name: 'Consolidate', count: sortedComponents.filter(c => c.recommendation === 'Consolidate').length, color: '#a78bfa' },
                  ]}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#8884d8" name="Count">
                    {sortedComponents.map((entry, index) => (
                      <Bar dataKey="count" fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
      
      {/* Export Options */}
      <div className="mt-4 flex space-x-2">
        <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
          Export to CSV
        </button>
        <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
          Export Chart as Image
        </button>
      </div>
    </div>
  );
};

export default EnhancedComponentEvaluationMatrix;