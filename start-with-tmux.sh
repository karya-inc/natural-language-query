#!/bin/sh

BACKEND_DIR=./backend/
FRONTEND_DIR=./frontend/
PORTAL_DIR=${PORTAL_DIR:-'../karya-server/server/'}
EDITOR=${EDITOR:-'nvim'}
IS_INIT_BACKEND=${IS_INIT_BACKEND:-'true'}

SESSION_NAME=${1:-'nlq'}
tmux new-session -d -s $SESSION_NAME
tmux rename-window -t $SESSION_NAME:0 'nvim'
tmux send-keys -t 'nvim' 'nvim' C-m

tmux new-window -t $SESSION_NAME:1 -n 'server'
tmux send-keys -t 'server' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "uvicorn server:app --port=5500 --reload" C-m

tmux new-window -t $SESSION_NAME:2 -n 'celery'
tmux send-keys -t 'celery' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "celery -A queues worker -l INFO" C-m

tmux new-window -t $SESSION_NAME:3 -n 'cron'
tmux send-keys -t 'cron' "cd $BACKEND_DIR" C-m ". env/bin/activate" C-m "python cron.py" C-m

tmux new-window -t $SESSION_NAME:4 -n 'frontend'
tmux send-keys -t 'frontend' "cd $FRONTEND_DIR" C-m "npm run dev" C-m

tmux new-window -t $SESSION_NAME:5 -n 'portal_frontend'
tmux send-keys -t 'portal_frontend' "cd $PORTAL_DIR/frontend" C-m "npm start" C-m

tmux new-window -t $SESSION_NAME:6 -n 'portal_backend'
tmux send-keys -t 'portal_backend' "cd $PORTAL_DIR/backend" c-m "node dist/Server.js" C-m
tmux select-window -t $SESSION_NAME:0

tmux new-window -t $SESSION_NAME:7 -n 'shell'

tmux attach -t $SESSION_NAME
