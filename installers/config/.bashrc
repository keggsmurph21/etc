
## BEGIN CUSTOM ##

# system
alias ls="ls -aF --color=auto"
alias inet="ip address | grep inet"
alias bashrc="vi ~/.bashrc && . ~/.bashrc"

# volume control
alias vu="amixer sset Master 5%+ > /dev/null"
alias vd="amixer sset Master 5%- > /dev/null"
alias vm="amixer sset Master 0% > /dev/null"

# programming langs
alias node=nodejs
alias python=python3

# git
alias gs="git status"
alias ga="git add"
alias gaa="git add -A"
alias gau="git add -u"
alias gc="git commit -m"
alias gco="git checkout"
alias gb="git checkout -b"
alias gp="git push"
alias gpu="git push --set-upstream origin `git branch | grep \* | cut -d ' ' -f2`"

## END CUSTOM ##
