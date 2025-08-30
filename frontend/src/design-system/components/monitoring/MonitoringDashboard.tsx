/**
 * Monitoring Dashboard Component
 * Displays comprehensive design system monitoring data
 */

import React, { useState, useEffect } from 'react';
import { generateMonitoringDashboard } from '../../monitoring';
import type { IntegrationReport, HealthScore, HealthAlert } from '../../monitoring';

interface MonitoringDashboardProps {
  refreshInterval?: number;
  showDetails?: boolean;
}

interface DashboardData {
  timestamp: number;
  performance: any;
  integration: IntegrationReport;
  accessibility: any;
  summary: {
    overallHealth: number;
    performanceScore: number;
    accessibilityScore: number;
    criticalIssues: number;
  };
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({
  refreshInterval = 60000, // 1 minute
  showDetails = true
}) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const dashboardData = await generateMonitoringDashboard();
        setData(dashboardData);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load monitoring data');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Set up refresh interval
    const interval = setInterval(fetchData, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading && !data) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <div className="text-red-600">
          <h3 className="text-lg font-semibold mb-2">Error Loading Monitoring Data</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Design System Monitoring</h2>
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdated?.toLocaleTimeString()}
            {loading && <span className="ml-2 text-blue-600">Refreshing...</span>}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className={`p-6 rounded-lg shadow ${getScoreBgColor(data.summary.overallHealth)}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Overall Health</p>
              <p className={`text-3xl font-bold ${getScoreColor(data.summary.overallHealth)}`}>
                {data.summary.overallHealth}%
              </p>
            </div>
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow ${getScoreBgColor(data.summary.performanceScore)}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Performance</p>
              <p className={`text-3xl font-bold ${getScoreColor(data.summary.performanceScore)}`}>
                {data.summary.performanceScore}%
              </p>
            </div>
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">⚡</span>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow ${getScoreBgColor(data.summary.accessibilityScore)}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Accessibility</p>
              <p className={`text-3xl font-bold ${getScoreColor(data.summary.accessibilityScore)}`}>
                {data.summary.accessibilityScore}%
              </p>
            </div>
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">♿</span>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow ${data.summary.criticalIssues > 0 ? 'bg-red-100' : 'bg-green-100'}`}>
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Critical Issues</p>
              <p className={`text-3xl font-bold ${data.summary.criticalIssues > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {data.summary.criticalIssues}
              </p>
            </div>
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">{data.summary.criticalIssues > 0 ? '🚨' : '✅'}</span>
            </div>
          </div>
        </div>
      </div>

      {showDetails && (
        <>
          {/* Health Score Breakdown */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Health Score Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(data.integration.healthScore).map(([key, score]) => (
                <div key={key} className="text-center">
                  <div className={`text-2xl font-bold ${getScoreColor(score)}`}>
                    {score}%
                  </div>
                  <div className="text-sm text-gray-600 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className={`h-2 rounded-full ${score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Alerts */}
          {data.integration.alerts.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Active Alerts</h3>
              <div className="space-y-3">
                {data.integration.alerts.slice(0, 10).map((alert: HealthAlert) => (
                  <div
                    key={alert.id}
                    className={`p-4 rounded-lg border-l-4 ${
                      alert.type === 'critical'
                        ? 'bg-red-50 border-red-400'
                        : alert.type === 'warning'
                        ? 'bg-yellow-50 border-yellow-400'
                        : 'bg-blue-50 border-blue-400'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className={`font-medium ${
                          alert.type === 'critical'
                            ? 'text-red-800'
                            : alert.type === 'warning'
                            ? 'text-yellow-800'
                            : 'text-blue-800'
                        }`}>
                          {alert.message}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          {alert.actionRequired}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          {formatTimestamp(alert.timestamp)} • {alert.category}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        alert.type === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : alert.type === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {alert.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Migration Progress */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Migration Progress</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {data.integration.metrics.migration.completedTasks}
                </div>
                <div className="text-sm text-gray-600">Completed Tasks</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-600">
                  {data.integration.metrics.migration.inProgressTasks}
                </div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {Math.round(data.integration.metrics.migration.overallProgress)}%
                </div>
                <div className="text-sm text-gray-600">Overall Progress</div>
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${data.integration.metrics.migration.overallProgress}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {data.integration.recommendations.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
              <div className="space-y-3">
                {data.integration.recommendations.slice(0, 5).map((rec, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-l-4 ${
                      rec.priority === 'high'
                        ? 'bg-red-50 border-red-400'
                        : rec.priority === 'medium'
                        ? 'bg-yellow-50 border-yellow-400'
                        : 'bg-green-50 border-green-400'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{rec.action}</p>
                        <p className="text-sm text-gray-600 mt-1">{rec.impact}</p>
                        <p className="text-xs text-gray-500 mt-2">{rec.category}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        rec.priority === 'high'
                          ? 'bg-red-100 text-red-800'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MonitoringDashboard;