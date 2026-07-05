import React,{useState,useEffect} from 'react';
import {LineChart,Line,XAxis,YAxis,CartesianGrid,Tooltip,ResponsiveContainer,PieChart,Pie,Cell} from 'recharts';

const API_BASE='http://localhost:8000';
const COLORS=['#3b82f6','#ef4444','#22c55e','#f59e0b','#8b5cf6'];

function App(){
  const [activeTab,setActiveTab]=useState('dashboard');
  const [stats,setStats]=useState(null);
  const [auditLogs,setAuditLogs]=useState([]);
  const [policies,setPolicies]=useState([]);
  const [approvals,setApprovals]=useState([]);
  const [selectedAgent,setSelectedAgent]=useState('default_agent');

  const fetchStats=async()=>{
    try{
      const res=await fetch(`${API_BASE}/api/v1/stats/${selectedAgent}`);
      setStats(await res.json());
    }catch(e){}
  };

  const fetchAudit=async()=>{
    try{
      const res=await fetch(`${API_BASE}/api/v1/audit/${selectedAgent}?limit=50`);
      setAuditLogs(await res.json());
    }catch(e){}
  };

  const fetchPolicies=async()=>{
    try{
      const res=await fetch(`${API_BASE}/api/v1/policies`);
      setPolicies((await res.json()).rules||[]);
    }catch(e){}
  };

  const fetchApprovals=async()=>{
    try{
      const res=await fetch(`${API_BASE}/api/v1/approvals`);
      setApprovals(await res.json());
    }catch(e){}
  };

  useEffect(()=>{
    fetchStats();fetchPolicies();
    const interval=setInterval(()=>{fetchStats();fetchAudit();fetchApprovals()},5000);
    return ()=>clearInterval(interval);
  },[]);

  const handleApprove=async(id)=>{
    await fetch(`${API_BASE}/api/v1/approvals/${id}/approve`,{method:'POST'});
    fetchApprovals();
  };

  const handleDeny=async(id)=>{
    await fetch(`${API_BASE}/api/v1/approvals/${id}/deny`,{method:'POST'});
    fetchApprovals();
  };

  const NavItem=({tab,icon,label})=>(
    <button
      onClick={()=>{setActiveTab(tab);if(tab==='audit')fetchAudit();if(tab==='approvals')fetchApprovals()}}
      style={{
        padding:'12px 20px',border:'none',background:activeTab===tab?'#1e293b':'transparent',
        color:activeTab===tab?'#3b82f6':'#94a3b8',cursor:'pointer',
        textAlign:'left',fontSize:'14px',borderRadius:'8px',
        display:'flex',alignItems:'center',gap:'10px',width:'100%'
      }}
    >
      <span style={{fontSize:'18px'}}>{icon}</span>
      {label}
    </button>
  );

  const budgetData=stats?[
    {name:'Daily Used',value:stats.daily_used},
    {name:'Daily Remaining',value:stats.daily_remaining},
  ]:[];

  const auditChartData=auditLogs.slice(0,20).reverse().map((l,i)=>({
    index:i,
    tokens:l.token_cost||0,
    duration:(l.duration||0)*1000
  }));

  return(
    <div style={{display:'flex',minHeight:'100vh'}}>
      {/* Sidebar */}
      <aside style={{
        width:'240px',background:'#1e293b',padding:'20px',
        display:'flex',flexDirection:'column',gap:'8px',
        borderRight:'1px solid #334155'
      }}>
        <div style={{padding:'12px 20px',marginBottom:'20px'}}>
          <h1 style={{fontSize:'22px',fontWeight:700,color:'#f8fafc',display:'flex',alignItems:'center',gap:'8px'}}>
            <span style={{color:'#3b82f6'}}>&#9670;</span> AegisFlow
          </h1>
        </div>
        <NavItem tab="dashboard" icon="&#9679;" label="Dashboard"/>
        <NavItem tab="audit" icon="&#9683;" label="Audit Trail"/>
        <NavItem tab="policies" icon="&#9636;" label="Policies"/>
        <NavItem tab="approvals" icon="&#9733;" label="Approvals"/>
        <NavItem tab="config" icon="&#9881;" label="Configuration"/>
      </aside>

      {/* Main */}
      <main style={{flex:1,padding:'30px',overflow:'auto'}}>
        {activeTab==='dashboard'&&(
          <div>
            <h2 style={{fontSize:'24px',marginBottom:'20px'}}>Agent Governance Dashboard</h2>
            <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'16px',marginBottom:'30px'}}>
              {[
                {label:'Daily Used',value:stats?`${(stats.daily_used/1000).toFixed(0)}K`:'-',sub:'tokens'},
                {label:'Daily Limit',value:stats?`${(stats.daily_limit/1e6).toFixed(1)}M`:'-',sub:'tokens'},
                {label:'Monthly Used',value:stats?`${(stats.monthly_used/1e6).toFixed(1)}M`:'-',sub:'tokens'},
                {label:'Active Sessions',value:'-',sub:'agents'},
              ].map((card,i)=>(
                <div key={i} style={{
                  background:'#1e293b',padding:'20px',borderRadius:'12px',
                  border:'1px solid #334155'
                }}>
                  <div style={{fontSize:'13px',color:'#94a3b8',marginBottom:'8px'}}>{card.label}</div>
                  <div style={{fontSize:'28px',fontWeight:700,color:'#f8fafc'}}>{card.value}</div>
                  <div style={{fontSize:'12px',color:'#64748b'}}>{card.sub}</div>
                </div>
              ))}
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'20px'}}>
              <div style={{background:'#1e293b',padding:'20px',borderRadius:'12px',border:'1px solid #334155'}}>
                <h3 style={{marginBottom:'15px'}}>Token Consumption Trend</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={auditChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155"/>
                    <XAxis dataKey="index" stroke="#64748b"/>
                    <YAxis stroke="#64748b"/>
                    <Tooltip contentStyle={{background:'#0f172a',border:'1px solid #334155'}}/>
                    <Line type="monotone" dataKey="tokens" stroke="#3b82f6" strokeWidth={2}/>
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div style={{background:'#1e293b',padding:'20px',borderRadius:'12px',border:'1px solid #334155'}}>
                <h3 style={{marginBottom:'15px'}}>Budget Allocation</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={budgetData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                      {budgetData.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                    </Pie>
                    <Tooltip contentStyle={{background:'#0f172a',border:'1px solid #334155'}}/>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab==='audit'&&(
          <div>
            <h2 style={{fontSize:'24px',marginBottom:'20px'}}>Audit Trail</h2>
            <div style={{background:'#1e293b',borderRadius:'12px',border:'1px solid #334155',overflow:'auto'}}>
              <table style={{width:'100%',borderCollapse:'collapse',fontSize:'14px'}}>
                <thead>
                  <tr style={{background:'#0f172a'}}>
                    {['Time','Agent','Action','Result','Tokens','Duration'].map(h=>(
                      <th key={h} style={{padding:'12px 16px',textAlign:'left',color:'#94a3b8',borderBottom:'1px solid #334155'}}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map(log=>(
                    <tr key={log.id} style={{borderBottom:'1px solid #1e293b'}}>
                      <td style={{padding:'12px 16px'}}>{new Date(log.timestamp*1000).toLocaleTimeString()}</td>
                      <td style={{padding:'12px 16px'}}>{log.agent_id}</td>
                      <td style={{padding:'12px 16px'}}>{log.action}</td>
                      <td style={{padding:'12px 16px'}}>
                        <span style={{
                          padding:'2px 8px',borderRadius:'4px',fontSize:'12px',
                          background:log.result==='success'?'#064e3b':log.result==='error'?'#450a0a':'#1e293b',
                          color:log.result==='success'?'#22c55e':log.result==='error'?'#ef4444':'#94a3b8'
                        }}>{log.result}</span>
                      </td>
                      <td style={{padding:'12px 16px'}}>{log.token_cost||0}</td>
                      <td style={{padding:'12px 16px'}}>{(log.duration*1000).toFixed(1)}ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab==='policies'&&(
          <div>
            <h2 style={{fontSize:'24px',marginBottom:'20px'}}>Policy Rules</h2>
            <div style={{display:'grid',gap:'12px'}}>
              {policies.map(p=>(
                <div key={p.name} style={{
                  background:'#1e293b',padding:'16px 20px',borderRadius:'12px',
                  border:'1px solid #334155',display:'flex',justifyContent:'space-between',alignItems:'center'
                }}>
                  <div>
                    <div style={{fontWeight:600,marginBottom:'4px'}}>{p.name}</div>
                    <div style={{fontSize:'13px',color:'#94a3b8'}}>{p.description}</div>
                  </div>
                  <div style={{display:'flex',gap:'8px',alignItems:'center'}}>
                    <span style={{
                      padding:'4px 10px',borderRadius:'6px',fontSize:'12px',
                      background:p.action==='allow'?'#064e3b':p.action==='deny'?'#450a0a':p.action==='human_loop'?'#1e3a5f':'#1e293b',
                      color:p.action==='allow'?'#22c55e':p.action==='deny'?'#ef4444':p.action==='human_loop'?'#3b82f6':'#94a3b8'
                    }}>{p.action}</span>
                    <span style={{
                      padding:'4px 10px',borderRadius:'6px',fontSize:'12px',
                      background:p.risk_level==='critical'?'#450a0a':p.risk_level==='high'?'#4a1a0a':'#1e293b',
                      color:p.risk_level==='critical'?'#ef4444':p.risk_level==='high'?'#f59e0b':'#94a3b8'
                    }}>{p.risk_level}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab==='approvals'&&(
          <div>
            <h2 style={{fontSize:'24px',marginBottom:'20px'}}>Pending Approvals</h2>
            {approvals.length===0&&(
              <div style={{color:'#64748b',textAlign:'center',padding:'40px'}}>No pending approvals</div>
            )}
            <div style={{display:'grid',gap:'12px'}}>
              {approvals.map(a=>(
                <div key={a.id} style={{
                  background:'#1e293b',padding:'20px',borderRadius:'12px',
                  border:'1px solid #334155',display:'flex',justifyContent:'space-between',alignItems:'center'
                }}>
                  <div>
                    <div style={{fontWeight:600,marginBottom:'4px'}}>{a.agent_id} — {a.action}</div>
                    <div style={{fontSize:'13px',color:'#94a3b8'}}>{a.reason}</div>
                  </div>
                  <div style={{display:'flex',gap:'8px'}}>
                    <button onClick={()=>handleApprove(a.id)} style={{
                      padding:'8px 20px',background:'#16a34a',color:'#fff',border:'none',
                      borderRadius:'8px',cursor:'pointer',fontWeight:600
                    }}>Approve</button>
                    <button onClick={()=>handleDeny(a.id)} style={{
                      padding:'8px 20px',background:'#dc2626',color:'#fff',border:'none',
                      borderRadius:'8px',cursor:'pointer',fontWeight:600
                    }}>Deny</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab==='config'&&(
          <div>
            <h2 style={{fontSize:'24px',marginBottom:'20px'}}>Configuration</h2>
            <div style={{background:'#1e293b',padding:'24px',borderRadius:'12px',border:'1px solid #334155'}}>
              <pre style={{fontSize:'14px',color:'#e2e8f0',whiteSpace:'pre-wrap'}}>
                {JSON.stringify({
                  api_host:'0.0.0.0',
                  api_port:8000,
                  budget:{daily_limit:'1,000,000 tokens',monthly_limit:'30,000,000 tokens'},
                  sandbox:{enabled:true,isolation_level:'moderate'},
                  compress:{enabled:true,target_ratio:'70%'},
                  audit:{enabled:true,retention:'90 days'},
                  human_loop:{enabled:true,timeout:'300s'}
                },null,2)}
              </pre>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
