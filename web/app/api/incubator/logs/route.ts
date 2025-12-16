import { NextResponse } from 'next/server';
import { join } from 'path';
import Database from 'better-sqlite3';

// Mark route as dynamic
export const dynamic = 'force-dynamic';

interface ObservationRow {
  id: number;
  agent_id: string;
  episode_id: string;
  timestamp: string;
  observation_text: string;
  action_code: string | null;
  outcome: string | null;
  reward: number;
  model_checkpoint: string;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');
    const agentId = searchParams.get('agent_id');

    // Path to the incubator observations database
    const dbPath = join(
      process.cwd(),
      '..',
      'src',
      'landscapes',
      'undergrowth',
      'incubator',
      'observations.db'
    );

    const db = new Database(dbPath, { readonly: true });

    // Build query
    let query = `
      SELECT
        id,
        agent_id,
        episode_id,
        timestamp,
        observation_text,
        action_code,
        outcome,
        reward,
        model_checkpoint
      FROM observations
    `;

    const params: any[] = [];

    if (agentId) {
      query += ' WHERE agent_id = ?';
      params.push(agentId);
    }

    query += ' ORDER BY timestamp DESC LIMIT ?';
    params.push(limit);

    const stmt = db.prepare(query);
    const observations = stmt.all(...params) as ObservationRow[];

    // Also get agent list
    const agentsQuery = `
      SELECT DISTINCT agent_id
      FROM observations
      ORDER BY agent_id
    `;
    const agents = db.prepare(agentsQuery).all() as { agent_id: string }[];

    db.close();

    return NextResponse.json({
      observations: observations.map((obs) => ({
        id: obs.id,
        agentId: obs.agent_id,
        episodeId: obs.episode_id,
        timestamp: obs.timestamp,
        observationText: obs.observation_text,
        actionCode: obs.action_code,
        outcome: obs.outcome,
        reward: obs.reward,
        modelCheckpoint: obs.model_checkpoint,
      })),
      agents: agents.map((a) => a.agent_id),
    });
  } catch (error) {
    console.error('Error loading incubator logs:', error);
    return NextResponse.json(
      {
        error: 'Failed to load logs',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
