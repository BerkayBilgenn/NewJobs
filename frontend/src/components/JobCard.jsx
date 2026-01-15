/**
 * JobCard Component
 * Displays a single job result with match score, company info, and apply button
 */

import React from 'react';

/**
 * Get color class based on match score
 * @param {number} score - Match score (0-100)
 * @returns {string} CSS class for the score badge
 */
const getScoreColor = (score) => {
  if (score >= 80) return 'score-excellent';
  if (score >= 50) return 'score-good';
  return 'score-weak';
};

/**
 * Get text color based on match score
 * @param {number} score - Match score (0-100)
 * @returns {string} Text description of match quality
 */
const getScoreLabel = (score) => {
  if (score >= 80) return 'Excellent Match';
  if (score >= 50) return 'Good Match';
  return 'Low Match';
};

const JobCard = ({ job }) => {
  const { title, company, link, image_url, match_score } = job;

  return (
    <div className="glass rounded-2xl p-6 hover:scale-[1.02] transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 group">
      {/* Match Score Badge */}
      <div className="flex justify-between items-start mb-4">
        <div className={`${getScoreColor(match_score)} px-3 py-1 rounded-full text-white text-sm font-bold shadow-lg`}>
          {match_score.toFixed(0)}% Match
        </div>
        <span className="text-xs text-gray-400">{getScoreLabel(match_score)}</span>
      </div>

      {/* Company Logo & Info */}
      <div className="flex items-start gap-4 mb-4">
        {image_url ? (
          <img 
            src={image_url} 
            alt={`${company} logo`}
            className="w-14 h-14 rounded-xl object-contain bg-white/10 p-2"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(company)}&background=3b82f6&color=fff&size=56`;
            }}
          />
        ) : (
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl">
            {company.charAt(0)}
          </div>
        )}
        
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
            {title}
          </h3>
          <p className="text-gray-400 text-sm truncate">{company}</p>
        </div>
      </div>

      {/* Match Score Bar */}
      <div className="mb-4">
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className={`h-full ${getScoreColor(match_score)} transition-all duration-500`}
            style={{ width: `${match_score}%` }}
          />
        </div>
      </div>

      {/* Apply Button */}
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="block w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-center py-3 px-4 rounded-xl font-medium transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/30"
      >
        Apply Now →
      </a>
    </div>
  );
};

export default JobCard;
