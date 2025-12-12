import { NextRequest, NextResponse } from 'next/server';
import { execSync } from 'child_process';

export async function GET(
  request: NextRequest,
  { params }: { params: { session: string } }
) {
  try {
    const { session } = params;
    const lines = request.nextUrl.searchParams.get('lines') || '50';

    // Capture last N lines from tmux session
    // -p: print to stdout
    // -e: include ANSI escape sequences (colors)
    // -S: start line (negative = from end)
    // -t: target session
    const command = `tmux capture-pane -t ${session} -p -e -S -${lines}`;
    const output = execSync(command, { encoding: 'utf-8' });

    return new Response(output, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
      },
    });
  } catch (error: any) {
    // Session might not exist or tmux error
    return NextResponse.json(
      { error: 'Failed to capture tmux output', details: error.message },
      { status: 500 }
    );
  }
}
