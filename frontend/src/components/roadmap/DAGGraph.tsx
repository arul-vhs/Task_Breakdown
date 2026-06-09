import React, { useMemo } from 'react';
import { TaskItem, DependencyItem } from '../../types/api';

interface DAGGraphProps {
  tasks: TaskItem[];
  dependencies: DependencyItem[];
}

export function DAGGraph({ tasks, dependencies }: DAGGraphProps) {
  const dag = useMemo(() => {
    if (!tasks || tasks.length === 0) {
      return { nodes: [], edges: [], width: 800, height: 350 };
    }

    const taskMap = new Map<string, TaskItem>();
    tasks.forEach(t => taskMap.set(t.task_id_alias, t));

    // Calculate topological levels
    const levels = new Map<string, number>();
    tasks.forEach(t => levels.set(t.task_id_alias, 0));
    
    let changed = true;
    let iterations = 0;
    while (changed && iterations < 100) {
      changed = false;
      iterations++;
      dependencies.forEach(dep => {
        const fromLevel = levels.get(dep.depends_on_alias) ?? 0;
        const toLevel = levels.get(dep.task_id_alias) ?? 0;
        if (toLevel <= fromLevel) {
          levels.set(dep.task_id_alias, fromLevel + 1);
          changed = true;
        }
      });
    }

    // Group tasks by topological columns
    const columns: string[][] = [];
    levels.forEach((level, alias) => {
      if (!columns[level]) columns[level] = [];
      columns[level].push(alias);
    });

    const activeColumns = columns.filter(col => col && col.length > 0);

    const colWidth = 220;
    const rowHeight = 100;
    const xOffset = 60;
    const yOffset = 40;
    
    const nodes: any[] = [];
    const nodeCoords = new Map<string, { x: number; y: number }>();

    const maxRows = Math.max(...activeColumns.map(col => col.length));
    const height = Math.max(350, maxRows * rowHeight + yOffset * 2);
    const width = Math.max(800, activeColumns.length * colWidth + xOffset * 2);

    activeColumns.forEach((colTasks, colIdx) => {
      const x = xOffset + colIdx * colWidth;
      const totalColHeight = colTasks.length * rowHeight;
      const colYOffset = (height - totalColHeight) / 2;

      colTasks.sort().forEach((alias, rowIdx) => {
        const y = colYOffset + rowIdx * rowHeight + (rowHeight / 2);
        const task = taskMap.get(alias);
        if (task) {
          nodes.push({
            id: alias,
            name: task.name || task.title,
            allocated_hours: task.allocated_hours,
            phase_name: task.phase_name,
            x,
            y
          });
          nodeCoords.set(alias, { x, y });
        }
      });
    });

    const edges: any[] = [];
    dependencies.forEach(dep => {
      const fromCoord = nodeCoords.get(dep.depends_on_alias);
      const toCoord = nodeCoords.get(dep.task_id_alias);
      
      if (fromCoord && toCoord) {
        edges.push({
          id: `${dep.depends_on_alias}-${dep.task_id_alias}`,
          from: fromCoord,
          to: toCoord,
          fromAlias: dep.depends_on_alias,
          toAlias: dep.task_id_alias
        });
      }
    });

    return { nodes, edges, width, height };
  }, [tasks, dependencies]);

  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-8 text-xs text-slate-500">
        No task blueprint generated to compute dependency logs.
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto bg-slate-950/45 p-6 rounded-2xl border border-slate-800/80 relative">
      <div className="absolute top-4 left-4 flex items-center space-x-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
        <span>Workflow Dependency Graph (DAG)</span>
      </div>

      <div style={{ width: `${dag.width}px`, height: `${dag.height}px` }} className="relative mx-auto mt-6">
        <svg style={{ width: `${dag.width}px`, height: `${dag.height}px` }} className="absolute inset-0 pointer-events-none">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#4338ca" />
            </marker>
          </defs>
          
          {dag.edges.map((edge) => {
            // Draw curved bezier line between node coordinates
            const dx = edge.to.x - edge.from.x;
            const controlX = edge.from.x + dx * 0.5;
            const path = `M ${edge.from.x} ${edge.from.y} C ${controlX} ${edge.from.y}, ${controlX} ${edge.to.y}, ${edge.to.x} ${edge.to.y}`;
            
            return (
              <path 
                key={edge.id}
                d={path}
                fill="transparent"
                stroke="#312e81"
                strokeWidth="2"
                markerEnd="url(#arrow)"
                className="transition duration-300 hover:stroke-indigo-500"
              />
            );
          })}
        </svg>

        {dag.nodes.map((node) => (
          <div
            key={node.id}
            style={{ 
              left: `${node.x - 90}px`, 
              top: `${node.y - 35}px`,
              width: '180px',
              height: '70px'
            }}
            className="absolute rounded-xl bg-slate-900/90 border border-slate-800 p-2.5 flex flex-col justify-between hover:border-indigo-500/80 hover:bg-slate-900 shadow-lg transition duration-200"
          >
            <div className="flex items-start justify-between">
              <span className="text-[9px] font-bold uppercase text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                {node.id}
              </span>
              <span className="text-[9px] text-slate-500 font-semibold">{node.allocated_hours}h</span>
            </div>
            <p className="text-[10px] text-slate-200 truncate font-semibold w-full mt-1.5" title={node.name}>
              {node.name}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
