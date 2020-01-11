#!/usr/bin/env bash
#
# GitHub Pages Deploy Script
#
# Usage:
#   deploy.sh [--debug] [<arg>]
#   deploy.sh --version
#   deploy.sh -h|--help
#
# Options:
#   --debug           Debug mode
#   --version         Print version
#   -h, --help        Print usage
#
# Arguments:
#   <arg>             Main arguments

set -ue

if [[ ${#} -ge 1 ]]; then
  for a in "${@}"; do
    [[ "${a}" = '--debug' ]] && set -x && break
  done
fi

SCRIPT_PATH=$(realpath "${0}")
SCRIPT_NAME=$(basename "${SCRIPT_PATH}")
SCRIPT_DIR_PATH=$(dirname "${SCRIPT_PATH}")
SCRIPT_VERSION='v0.0.1'
GH_PAGES_BRANCH='gh-pages'
GH_REMOTE_URL=$(
  grep -2 -e '\[remote "origin"\]' "${SCRIPT_DIR_PATH}/.git/config" \
    | grep -e 'url =' \
    | awk '{print $3}'
)
HTML_DIR_PATH='./html'
MAIN_ARGS=()

function print_version {
  echo "${SCRIPT_NAME}: ${SCRIPT_VERSION}"
}

function print_usage {
  sed -ne '1,2d; /^#/!q; s/^#$/# /; s/^# //p;' "${SCRIPT_PATH}"
}

function abort {
  {
    if [[ ${#} -eq 0 ]]; then
      cat -
    else
      SCRIPT_NAME=$(basename "${SCRIPT_PATH}")
      echo "${SCRIPT_NAME}: ${*}"
    fi
  } >&2
  exit 1
}

while [[ ${#} -ge 1 ]]; do
  case "${1}" in
    '--debug' )
      shift 1
      ;;
    '--version' )
      print_version && exit 0
      ;;
    '-h' | '--help' )
      print_usage && exit 0
      ;;
    -* )
      abort "invalid option: ${1}"
      ;;
    * )
      MAIN_ARGS+=("${1}") && shift 1
      ;;
  esac
done

if [[ ${#MAIN_ARGS[@]} -gt 1 ]]; then
  abort "$(print_usage)"
elif [[ ${#MAIN_ARGS[@]} -eq 1 ]]; then
  HTML_DIR_PATH="${MAIN_ARGS[0]}"
fi

printf "GH_REMOTE_URL:  \t%s\n" "${GH_REMOTE_URL}"
printf "GH_PAGES_BRANCH:\t%s\n" "${GH_PAGES_BRANCH}"
printf "HTML_DIR_PATH:  \t%s\n" "${HTML_DIR_PATH}"
git --version

cd "${HTML_DIR_PATH}"
[[ -d '.git' ]] && rm -rf .git
git init
git add .
git commit -m 'Deploy HTML documents'
git push -f "${GH_REMOTE_URL}" master:"${GH_PAGES_BRANCH}"
rm -rf .git
