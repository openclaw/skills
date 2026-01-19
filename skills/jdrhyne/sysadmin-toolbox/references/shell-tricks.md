#### Shell Tricks &nbsp;[<sup>[TOC]</sup>](#anger-table-of-contents)

When you get a shell, it is generally not very clean, but after following these steps, you will have a fairly clean and comfortable shell to work with.

1) `script /dev/null -c bash`
2) Ctrl-Z (to send it to background)
3) `stty raw -echo; fg` (returns the shell to foreground)
4) `reset` (to reset terminal)
5) `xterm` (when asked for terminal type)
6) `export TERM=xterm; export SHELL=bash`

#### Shell functions &nbsp;[<sup>[TOC]</sup>](#anger-table-of-contents)

##### Table of Contents

- [Domain resolve](#domain-resolve)
- [Get ASN](#get-asn)

###### Domain resolve

```bash
# Dependencies:
#   - curl
#   - jq

function DomainResolve() {

  local _host="$1"

  local _curl_base="curl --request GET"
  local _timeout="15"

  _host_ip=$($_curl_base -ks -m "$_timeout" "https://dns.google.com/resolve?name=${_host}&type=A" | \
  jq '.Answer[0].data' | tr -d "\"" 2>/dev/null)

  if [[ -z "$_host_ip" ]] || [[ "$_host_ip" == "null" ]] ; then

    echo -en "Unsuccessful domain name resolution.\\n"

  else

    echo -en "$_host > $_host_ip\\n"

  fi

}
```

Example:

```bash
shell> DomainResolve nmap.org
nmap.org > 45.33.49.119

shell> DomainResolve nmap.org
Unsuccessful domain name resolution.
```

###### Get ASN

```bash
# Dependencies:
#   - curl

function GetASN() {

  local _ip="$1"

  local _curl_base="curl --request GET"
  local _timeout="15"

  _asn=$($_curl_base -ks -m "$_timeout" "http://ip-api.com/line/${_ip}?fields=as")

  _state=$(echo $?)

  if [[ -z "$_ip" ]] || [[ "$_ip" == "null" ]] || [[ "$_state" -ne 0 ]]; then

    echo -en "Unsuccessful ASN gathering.\\n"

  else

    echo -en "$_ip > $_asn\\n"

  fi

}
```

Example:

```bash
shell> GetASN 1.1.1.1
1.1.1.1 > AS13335 Cloudflare, Inc.

shell> GetASN 0.0.0.0
Unsuccessful ASN gathering.
```
