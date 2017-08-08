# PkmNotifier

A Notifier for Pokemon Go.

## Useage

1. Apply a [Twilio](https://www.twilio.com/) account, and copy your API token into `config.py`:
```python
sid = 'your twilio sid'
token = 'your twilio token'
from_number = 'your twilio phone number'
to_number = 'your phone number'
addr = 'your address'
```

2. Uncomment your favorite Pokemons in `pkmid.py`

3. Run the `pkmnotifier.py`! (You can also run it with `cron_mode`)

4. Wait for SMS and meet your Pokemons!
