# py-mco-agent

## Overview

`py-mco-agent` contains a collection of tools for writing mcollective agents in the Python language.

## Installation

    pip install py-mco-agent
    
This library requires a version of Choria with external agent support.
    
## Implementing Agents

The bare minimum steps to implement a python mcollective agent are:

* Add a python file without a `.py` extension to `/opt/puppetlabs/mcollective/plugins/mcollective/agent/parrot`

```python
    #!/usr/bin/python3
    from mco_agent import Agent, action, dispatch, register_actions

    # Subclass Agent and decorate it with the @register_actions
    @register_actions
    class Parrot(Agent):
    
        # Create a class method for your action and decorate it with @action
        @action
        def echo(self):
            # This example action just repeats the message input back to the caller
            prefix = self.config.get('prefix', '')
            if not prefix:
                self.logger.warning("Using default prefix!")
            self.reply.data['message'] = prefix + self.request.data['message']

    if __name__ == '__main__':
        dispatch(Parrot)
```
        
* Add a choria JSON DDL file to the same location named `parrot.json` (see `examples/parrot.json`)

## Reference

### Agent

Provides a base class for implementing mcollective agents

Public methods:

- `should_activate`
  Returns a boolean value to indicate whether the agent should be activated on this host.
  By default returns True and the agent is always activated. Subclasses may choose to override
  this method and deactivate themselves under appropriate conditions such as missing pre-requisites.
  
Decorators:

- `@action`
  Instance methods should be decorated with the `@action` decorator to register them as available agent actions
- `@register_actions`
  The plugin class should be decorated with this method to trigger registration all action methods within
  
Instance variables:

- `logger`
  Contains a python logger which can be used to send log information back to choria (debug and info are sent to stdout,
  which is only displayed in verbose mode; warnings and errors are sent to stderr which are displayed always).
  The logger is set to use the `mcorpc.agent_name` hierarchy. By default all other logging is disabled to prevent
  pollution of the mcorpc reply. This is done by setting the log level on the root logger to 100. You can re-enable
  logging by adjusting the log-level on either the root logger or a specific child if required.
- `config`
  Contains a dict-like object which can be used to read configuration settings from the agent's choria plugin
  configuration file (`/etc/puppetlabs/mcollective/plugin.d/agentname.cfg` by default).
  
