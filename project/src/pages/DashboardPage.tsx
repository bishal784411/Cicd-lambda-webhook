import React, { useEffect, useRef, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Activity,
  CheckCircle,
  AlertTriangle,
  Container,
  GitBranch,
  Zap,
  Clock,
  Users,
  Server,
  Shield,
  Rocket,
  Pause,
  Play,
  Square,
  Terminal,
  Trash2,
} from 'lucide-react';
import { StatsCard } from '../components/StatsCard';
import { SystemHealth } from '../components/SystemHealth';
import { ProcessFlowMap } from '../components/ProcessFlowMap';
import { Breadcrumbs } from '../components/Breadcrumbs';
import { LiveNetworkStatus } from '../components/LiveNetworkStatus';
import { startagent, stopagent } from '../api/dashboard';

interface Metrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_pipelines: number;
  docker_containers_running: number;
  successful_deployments_today: number;
  failed_builds_today: number;
}

export const DashboardPage: React.FC = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalContent, setTerminalContent] = useState<string[]>([]);

  // Ref to hold AbortController to cancel streaming fetch on stop
  const streamControllerRef = useRef<AbortController | null>(null);

  // Live metrics state
  const [metrics, setMetrics] = useState<Metrics>({
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    active_pipelines: 8,
    docker_containers_running: 24,
    successful_deployments_today: 12,
    failed_builds_today: 3,
  });

  // Other system statuses (can be fetched from other APIs or mocked here)
  const [systemHealth] = useState<'healthy' | 'degraded' | 'critical'>('healthy');
  const [agentStatus] = useState<'active' | 'idle' | 'error' | 'maintenance'>('active');
  const [pipelineStatus] = useState<'running' | 'idle' | 'failed' | 'success'>('running');
  const [loading, setLoading] = useState(true);

  const currentPage = "dashboard";

  useEffect(() => {
    const eventSource = new EventSource(`${import.meta.env.VITE_API_BASE_URL}/system/usages`);

    eventSource.onmessage = (event) => {
      try {
        let raw = event.data.trim();
        if (raw.startsWith("data: ")) raw = raw.slice(6);
        const fixed = raw.replace(/'/g, '"');
        const data = JSON.parse(fixed);

        setMetrics((prev) => ({
          ...prev,
          cpu_usage: data.cpu_percent,
          memory_usage: data.memory_percent,
          disk_usage: data.disk_percent,
          active_pipelines: prev.active_pipelines,
          docker_containers_running: prev.docker_containers_running,
          successful_deployments_today: prev.successful_deployments_today,
          failed_builds_today: prev.failed_builds_today,
        }));

        setLoading(false);
      } catch (err) {
        console.error("Error parsing SSE data:", err, event.data);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  // const handleStartMonitor = async () => {
  //   try {
  //     await startagent();
  //     setIsMonitoring(true);
  //     setShowTerminal(true);

  //     // Clear terminal before streaming new logs
  //     setTerminalContent([]);

  //   } catch (err) {
  //     console.error('Failed to start monitor:', err);
  //   }
  // };

  // // Stop monitoring: call API, close SSE log stream
  // const handleStopMonitor = async () => {
  //   try {
  //     await stopagent();
  //     setIsMonitoring(false);


  //     setTerminalContent(prev => [
  //       ...prev,
  //       '',
  //       '[MONITOR STOPPED] Refer to the cards below in the CI/CD Pipeline Components section for detailed information.',
  //       ''
  //     ]);
  //   } catch (err) {
  //     console.error('Failed to stop monitor:', err);
  //   }
  // };

  // Clear terminal and close stream if open
  
   const handleStartMonitor = async () => {
    setTerminalContent([]);
    setShowTerminal(true);
    setIsMonitoring(true);

    // Create AbortController to cancel fetch when stopping
    const controller = new AbortController();
    streamControllerRef.current = controller;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/agents/start-all`, {
        method: 'POST',
        signal: controller.signal,
      });

      if (!response.body) {
        throw new Error('ReadableStream not supported in this browser');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line);
              // Append formatted output to terminal content
              setTerminalContent(prev => [
                ...prev,
                formatLogLine(json),
              ]);
            } catch (err) {
              // If invalid JSON, ignore or optionally add raw line
              // setTerminalContent(prev => [...prev, line]);
            }
          }
        }
      }
    } catch (err) {
      if ((err as any).name !== 'AbortError') {
        console.error('Stream error:', err);
        setTerminalContent(prev => [...prev, '[ERROR] Stream failed or disconnected']);
      }
    } finally {
      setIsMonitoring(false);
      setTerminalContent(prev => [...prev, '[STREAM ENDED]']);
      streamControllerRef.current = null;
    }
  };

  const handleStopMonitor = async () => {
    // Abort streaming fetch if active
    if (streamControllerRef.current) {
      streamControllerRef.current.abort();
      streamControllerRef.current = null;
    }

    try {
      await stopagent();
    } catch (err) {
      console.error('Failed to stop monitor:', err);
    }

    setIsMonitoring(false);
    setTerminalContent(prev => [
      ...prev,
      '',
      '[MONITOR STOPPED] Refer to the cards below in the CI/CD Pipeline Components section for detailed information.',
      '',
    ]);
  };

  // Helper function to format JSON log line into readable string
  const formatLogLine = (logObj: any) => {
    if (logObj.output) {
      return logObj.output;
    }
    if (logObj.status) {
      return `[${logObj.agent}] STATUS: ${logObj.status}`;
    }
    if (logObj.result) {
      return `[${logObj.agent}] RESULT: ${logObj.result}`;
    }
    if (logObj.agent && logObj.output) {
      return `[${logObj.agent}] ${logObj.output}`;
    }
    return JSON.stringify(logObj);
  };

  const handleClearTerminal = async () => {
    setTerminalContent([]);
    await stopagent();
    setIsMonitoring(false);
    setShowTerminal(false);

  };




  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center space-x-3 text-cyan-300">
          <BarChart3 className="h-6 w-6 animate-pulse" />
          <span className="text-lg">Loading dashboard metrics...</span>
        </div>
      </div>
    );
  }

  // Mock agent and deployment data (or replace with real API data)
  const mockAgentData = {
    totalAgents: 3,
    activeAgents: 3,
    agentsWithIssues: 1,
  };

  const mockDeploymentData = {
    successfulDeployments: metrics.successful_deployments_today,
    failedDeployments: metrics.failed_builds_today,
    totalPipelines: metrics.active_pipelines,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <Breadcrumbs currentPage={currentPage} parentPage="dashboard" />

      {/* Monitor Control Section */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <Terminal className="h-5 w-5 mr-2 text-green-400" />
            Agent Control
          </h3>
          <div className="flex items-center space-x-3">
            {!isMonitoring ? (
              <button
                onClick={handleStartMonitor}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                <Play className="h-4 w-4" />
                <span>Start All Agent</span>
              </button>
            ) : (
              <button
                onClick={handleStopMonitor}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                <Square className="h-4 w-4" />
                <span>Stop All Agent</span>
              </button>
            )}

            {showTerminal && (
              <button
                onClick={handleClearTerminal}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                <span>Close Terminal</span>
              </button>
            )}
          </div>
        </div>

        {!isMonitoring && !showTerminal && (
          <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-xl p-4">
            <div className="flex items-center space-x-2">
              <Pause className="h-5 w-5 text-yellow-400" />
              <span className="text-yellow-300 font-medium">Pipeline Paused</span>
            </div>
            <p className="text-yellow-200 mt-1">
              Click ‘Start All Agent to initiate monitoring of your workflow.
            </p>
          </div>
        )}

        {/* Terminal Window */}
        {showTerminal && (
          <div className="bg-black rounded-lg border border-gray-600 overflow-hidden resize-y min-h-[200px] max-h-[80vh] mt-3">
            {/* Terminal Header */}
            <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-600 cursor-default">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-300 text-sm ml-2">CI/CD Terminal</span>
              </div>
            </div>

            {/* Terminal Content (scrollable inside) */}
            <div
              className="p-4 font-mono text-sm overflow-y-auto"
              style={{ height: 'calc(100% - 40px)' }} // subtract header height (40px)
              ref={(el) => {
                if (el) el.scrollTop = el.scrollHeight;
              }}
            >
              {terminalContent.length === 0 ? (
                <div className="text-green-400">
                  $ Starting CI/CD monitoring system...
                  <br />
                  $ Initializing log stream...
                  <br />
                  <span className="animate-pulse">$ Waiting for log entries...</span>
                </div>
              ) : (
                <div className="space-y-1">
                  {(() => {
                    const elements: JSX.Element[] = [];
                    let insideCodeBlock = false;
                    let codeBlockLang = '';
                    let codeLines: string[] = [];

                    terminalContent.forEach((line, index) => {
                      if (line.trim().startsWith('```')) {
                        if (!insideCodeBlock) {
                          insideCodeBlock = true;
                          codeBlockLang = line.trim().slice(3).trim();
                          codeLines = [];
                        } else {
                          insideCodeBlock = false;
                          elements.push(
                            <pre
                              key={`code-${index}`}
                              className="bg-gray-900 text-green-300 text-sm p-3 rounded-md overflow-x-auto"
                            >
                              <code className={`language-${codeBlockLang}`}>
                                {codeLines.join('\n')}
                              </code>
                            </pre>
                          );
                        }
                      } else if (insideCodeBlock) {
                        codeLines.push(line.replace(/^OUT:\s?/, ''));
                      } else {
                        const content = line.replace(/^OUT:\s?/, '');
                        let colorClass = 'text-gray-300';
                        if (line.includes('ERROR')) colorClass = 'text-red-400';
                        else if (line.includes('WARN')) colorClass = 'text-yellow-400';
                        else if (line.includes('SUCCESS')) colorClass = 'text-green-400';
                        else if (line.includes('MONITOR STOPPED')) colorClass = 'text-cyan-400 font-bold';

                        elements.push(
                          <div key={index} className={colorClass}>
                            {content}
                          </div>
                        );
                      }
                    });

                    if (isMonitoring) {
                      elements.push(
                        <div key="active-monitor" className="text-green-400 animate-pulse">
                          $ Monitoring active...
                        </div>
                      );
                    }

                    return elements;
                  })()}
                </div>
              )}
            </div>
          </div>
        )}



      </div>

      {/* System Health Overview */}
      <SystemHealth
        metrics={metrics}
        systemHealth={systemHealth}
        agentStatus={agentStatus}
        pipelineStatus={pipelineStatus}
      />

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Agents"
          value={mockAgentData.totalAgents}
          icon={Users}
          color="bg-blue-500/20 text-blue-400"
          subtitle={`${mockAgentData.activeAgents} active`}
          trend={{ value: 8.2, isPositive: true }}
        />

        <StatsCard
          title="Successful Deployments"
          value={mockDeploymentData.successfulDeployments}
          icon={CheckCircle}
          color="bg-green-500/20 text-green-400"
          subtitle="Today's successful deployments"
          trend={{ value: 15.3, isPositive: true }}
        />

        <StatsCard
          title="Pipeline Files Monitored"
          value={mockDeploymentData.totalPipelines}
          icon={GitBranch}
          color="bg-purple-500/20 text-purple-400"
          subtitle="Docker, K8s, CI/CD configs"
          trend={{ value: 2.1, isPositive: true }}
        />

        <StatsCard
          title="Critical Issues"
          value={4} // Replace with real critical issues count if available
          icon={AlertTriangle}
          color="bg-red-500/20 text-red-400"
          subtitle="Requiring immediate attention"
          trend={{ value: 12.5, isPositive: false }}
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Active Pipelines"
          value={mockDeploymentData.totalPipelines}
          icon={Activity}
          color="bg-cyan-500/20 text-cyan-400"
          subtitle="Currently running"
        />



        <StatsCard
          title="Failed Builds Today"
          value={mockDeploymentData.failedDeployments}
          icon={AlertTriangle}
          color="bg-orange-500/20 text-orange-400"
          subtitle="Build failures"
        />

        <StatsCard
          title="System Uptime"
          value="99.8%"
          icon={TrendingUp}
          color="bg-emerald-500/20 text-emerald-400"
          subtitle="Last 30 days"
        />
      </div>

      {/* Quick Actions & Recent Activity */}


      {/* Network Status */}
      <LiveNetworkStatus />

      {/* Process Flow Map */}
      <ProcessFlowMap />
    </div>
  );
};
