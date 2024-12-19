#!/bin/sh

BACKEND_DIR=./backend/
FRONTEND_DIR=./frontend/
PORTAL_DIR=${PORTAL_DIR:-'../karya-server/server/'}
PORTAL_PORT=${PORTAL_PORT:-'8000'}
EDITOR=${EDITOR:-'nvim'}
IS_INIT_BACKEND=${IS_INIT_BACKEND:-'true'}


SESSION_NAME=${1:-'nlq'}

IS_SESSION_STARTED=$(tmux list-sessions 2> /dev/null | grep $SESSION_NAME | wc -l)

if [ $IS_SESSION_STARTED -gt 0 ]; then
  echo "Session with '$SESSION_NAME' already exists. Try using a different name by passing it as an argument."
  exit 1
fi


tmux new-session -d -s $SESSION_NAME
tmux rename-window -t $SESSION_NAME:0 'editor'
tmux send-keys -t 'editor' ". env/bin/activate" "$EDITOR ." C-m

tmux new-window -t $SESSION_NAME:1 -n 'server'
tmux send-keys -t 'server' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "uvicorn server:app --port=5500 --reload" C-m

tmux new-window -t $SESSION_NAME:2 -n 'celery'
tmux send-keys -t 'celery' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "celery -A queues worker -l INFO" C-m

tmux new-window -t $SESSION_NAME:3 -n 'cron'
tmux send-keys -t 'cron' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "python cron.py" C-m

tmux new-window -t $SESSION_NAME:4 -n 'frontend'
tmux send-keys -t 'frontend' "cd $FRONTEND_DIR" C-m "npm run dev" C-m

tmux new-window -t $SESSION_NAME:5 -n 'portal_frontend'
tmux send-keys -t 'portal_frontend' "cd $PORTAL_DIR/frontend" C-m "PORT=$PORTAL_PORT npm start" C-m

tmux new-window -t $SESSION_NAME:6 -n 'portal_backend'
tmux send-keys -t 'portal_backend' "cd $PORTAL_DIR/backend" c-m "node dist/Server.js" C-m

tmux new-window -t $SESSION_NAME:7 -n 'shell'

tmux select-window -t $SESSION_NAME:0
tmux attach -t $SESSION_NAME
