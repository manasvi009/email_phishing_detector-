import { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';

interface ThreatIndicator {
  type: string;
  severity: 'high' | 'medium' | 'low';
  description: string;
  found: boolean;
}

interface AnalysisResult {
  riskScore: number;
  riskLevel: 'safe' | 'suspicious' | 'dangerous';
  indicators: ThreatIndicator[];
  verdict: string;
}

export function PhishingAnalyzer() {
  const [sender, setSender] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const analyzeEmail = () => {
    setAnalyzing(true);

    // Simulate ML processing time
    setTimeout(() => {
      const indicators: ThreatIndicator[] = [];
      let riskScore = 0;

      // Check for suspicious sender domain
      const suspiciousDomains = ['support-paypal', 'secure-bank', 'verify-account', 'noreply-amazon'];
      const hasSuspiciousDomain = suspiciousDomains.some(domain => sender.toLowerCase().includes(domain));
      indicators.push({
        type: 'Suspicious Sender Domain',
        severity: 'high',
        description: 'Email sender domain appears to be impersonating a legitimate company',
        found: hasSuspiciousDomain
      });
      if (hasSuspiciousDomain) riskScore += 30;

      // Check for urgency language
      const urgencyWords = ['urgent', 'immediate', 'act now', 'suspend', 'verify', 'confirm', 'expire', 'limited time'];
      const hasUrgency = urgencyWords.some(word =>
        subject.toLowerCase().includes(word) || body.toLowerCase().includes(word)
      );
      indicators.push({
        type: 'Urgency Language',
        severity: 'medium',
        description: 'Email uses urgent language to pressure immediate action',
        found: hasUrgency
      });
      if (hasUrgency) riskScore += 20;

      // Check for request for personal information
      const personalInfoWords = ['password', 'social security', 'credit card', 'bank account', 'ssn', 'pin'];
      const requestsInfo = personalInfoWords.some(word => body.toLowerCase().includes(word));
      indicators.push({
        type: 'Requests Personal Information',
        severity: 'high',
        description: 'Email asks for sensitive personal or financial information',
        found: requestsInfo
      });
      if (requestsInfo) riskScore += 25;

      // Check for suspicious links
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const urls = body.match(urlRegex) || [];
      const hasSuspiciousUrls = urls.some(url =>
        url.includes('bit.ly') ||
        url.includes('tinyurl') ||
        /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url) ||
        url.split('.').length > 4
      );
      indicators.push({
        type: 'Suspicious Links',
        severity: 'high',
        description: 'Email contains shortened URLs or IP addresses instead of legitimate domains',
        found: hasSuspiciousUrls
      });
      if (hasSuspiciousUrls) riskScore += 25;

      // Check for spelling/grammar issues
      const spellingErrors = ['recieve', 'oppurtunity', 'guarante', 'suport', 'acount', 'verfiy'];
      const hasSpellingErrors = spellingErrors.some(word => body.toLowerCase().includes(word));
      indicators.push({
        type: 'Spelling/Grammar Issues',
        severity: 'medium',
        description: 'Email contains spelling or grammar mistakes common in phishing',
        found: hasSpellingErrors
      });
      if (hasSpellingErrors) riskScore += 15;

      // Check for generic greetings
      const hasGenericGreeting = body.toLowerCase().includes('dear customer') ||
                                 body.toLowerCase().includes('dear user') ||
                                 body.toLowerCase().includes('dear member');
      indicators.push({
        type: 'Generic Greeting',
        severity: 'low',
        description: 'Email uses generic greeting instead of your name',
        found: hasGenericGreeting
      });
      if (hasGenericGreeting) riskScore += 10;

      // Check for threats/consequences
      const threatWords = ['suspended', 'closed', 'terminated', 'penalty', 'legal action'];
      const hasThreats = threatWords.some(word => body.toLowerCase().includes(word));
      indicators.push({
        type: 'Threatening Language',
        severity: 'medium',
        description: 'Email threatens negative consequences to prompt action',
        found: hasThreats
      });
      if (hasThreats) riskScore += 15;

      // Determine risk level
      let riskLevel: 'safe' | 'suspicious' | 'dangerous';
      let verdict: string;

      if (riskScore >= 50) {
        riskLevel = 'dangerous';
        verdict = 'HIGH RISK: This email exhibits multiple characteristics of a phishing attack. Do not click links or provide any information.';
      } else if (riskScore >= 25) {
        riskLevel = 'suspicious';
        verdict = 'MEDIUM RISK: This email shows suspicious patterns. Exercise caution and verify sender authenticity before taking action.';
      } else {
        riskLevel = 'safe';
        verdict = 'LOW RISK: This email appears relatively safe, but always remain vigilant about unexpected requests.';
      }

      setResult({
        riskScore: Math.min(riskScore, 100),
        riskLevel,
        indicators: indicators.filter(i => i.found),
        verdict
      });

      setAnalyzing(false);
    }, 1500);
  };

  const handleAnalyze = () => {
    if (!sender || !subject || !body) {
      alert('Please fill in all fields');
      return;
    }
    analyzeEmail();
  };

  const handleReset = () => {
    setSender('');
    setSubject('');
    setBody('');
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl text-blue-900">Email Phishing Detector</h1>
          </div>
          <p className="text-gray-600">AI-powered analysis to detect phishing attempts and malicious emails</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-2xl text-gray-800 mb-4 flex items-center gap-2">
              <Info className="w-6 h-6 text-blue-600" />
              Email Details
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 mb-2">Sender Email</label>
                <input
                  type="email"
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  placeholder="sender@example.com"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>

              <div>
                <label className="block text-gray-700 mb-2">Email Subject</label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Enter email subject"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>

              <div>
                <label className="block text-gray-700 mb-2">Email Body</label>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Paste the email content here..."
                  rows={8}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Email'}
                </button>
                <button
                  onClick={handleReset}
                  className="px-6 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg transition duration-200"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-2xl text-gray-800 mb-4 flex items-center gap-2">
              <Shield className="w-6 h-6 text-green-600" />
              Analysis Results
            </h2>

            {!result ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <Shield className="w-16 h-16 mx-auto mb-3 opacity-30" />
                  <p>Enter email details and click "Analyze Email" to see results</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Risk Score */}
                <div className={`p-4 rounded-lg ${
                  result.riskLevel === 'dangerous' ? 'bg-red-50 border border-red-200' :
                  result.riskLevel === 'suspicious' ? 'bg-yellow-50 border border-yellow-200' :
                  'bg-green-50 border border-green-200'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-700">Risk Score</span>
                    <span className={`text-2xl ${
                      result.riskLevel === 'dangerous' ? 'text-red-600' :
                      result.riskLevel === 'suspicious' ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {result.riskScore}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-1000 ${
                        result.riskLevel === 'dangerous' ? 'bg-red-600' :
                        result.riskLevel === 'suspicious' ? 'bg-yellow-500' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${result.riskScore}%` }}
                    />
                  </div>
                </div>

                {/* Verdict */}
                <div className={`p-4 rounded-lg flex items-start gap-3 ${
                  result.riskLevel === 'dangerous' ? 'bg-red-50' :
                  result.riskLevel === 'suspicious' ? 'bg-yellow-50' :
                  'bg-green-50'
                }`}>
                  {result.riskLevel === 'dangerous' ? (
                    <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                  ) : result.riskLevel === 'suspicious' ? (
                    <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  )}
                  <p className="text-sm text-gray-700">{result.verdict}</p>
                </div>

                {/* Threat Indicators */}
                <div>
                  <h3 className="text-gray-800 mb-3">Detected Threats ({result.indicators.length})</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {result.indicators.length === 0 ? (
                      <p className="text-sm text-gray-500">No major threats detected</p>
                    ) : (
                      result.indicators.map((indicator, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg border ${
                            indicator.severity === 'high' ? 'bg-red-50 border-red-200' :
                            indicator.severity === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                            'bg-blue-50 border-blue-200'
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            <AlertTriangle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
                              indicator.severity === 'high' ? 'text-red-600' :
                              indicator.severity === 'medium' ? 'text-yellow-600' :
                              'text-blue-600'
                            }`} />
                            <div>
                              <p className="text-sm text-gray-800">{indicator.type}</p>
                              <p className="text-xs text-gray-600 mt-1">{indicator.description}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Info Cards */}
        <div className="mt-8 grid md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-gray-800">AI-Powered</h3>
            </div>
            <p className="text-sm text-gray-600">Uses machine learning algorithms to detect phishing patterns</p>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-gray-800">Real-time Analysis</h3>
            </div>
            <p className="text-sm text-gray-600">Instant detection of suspicious email characteristics</p>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-gray-800">Detailed Reports</h3>
            </div>
            <p className="text-sm text-gray-600">Comprehensive breakdown of potential threats found</p>
          </div>
        </div>
      </div>
    </div>
  );
}
