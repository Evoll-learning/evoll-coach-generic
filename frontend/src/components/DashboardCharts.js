import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from 'recharts';

// Circular Progress Component
export const CircularProgress = ({ percentage, size = 200, strokeWidth = 20 }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1A2F47"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="url(#greenGradient)"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
          style={{ strokeDashoffset: offset }}
        />
        <defs>
          <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#2D9B4E" />
            <stop offset="100%" stopColor="#4FD670" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-5xl font-bold text-white">{percentage}%</span>
      </div>
    </div>
  );
};

// Horizontal Bar Chart Component
export const HorizontalMetricBar = ({ label, value, maxValue = 100 }) => {
  const percentage = (value / maxValue) * 100;
  
  return (
    <div className="space-y-2" data-testid={`metric-bar-${label}`}>
      <div className="flex justify-between items-center">
        <span className="text-gray-300 font-medium">{label}</span>
        <span className="text-2xl font-bold text-white">{value}%</span>
      </div>
      <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Pie Chart for Distribution
export const DistributionPieChart = ({ data, colors }) => {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
};

// Module Performance Bars
export const ModulePerformanceBars = ({ modules }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={modules} layout="vertical" margin={{ left: 20, right: 20 }}>
        <XAxis type="number" domain={[0, 100]} stroke="#9CA3AF" />
        <YAxis type="category" dataKey="name" stroke="#9CA3AF" width={120} />
        <Bar dataKey="score" fill="url(#barGradient)" radius={[0, 8, 8, 0]}>
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#2D9B4E" />
              <stop offset="100%" stopColor="#4FD670" />
            </linearGradient>
          </defs>
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
