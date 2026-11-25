# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.data.database import get_db_session

class BaseDataService:
    """
    Base service class that handles database session management.
    All specialized data services should inherit from this class.
    """
    def __init__(self, db_session: Session = None):
        self._db_session = db_session

    @contextmanager
    def _get_db(self):
        """
        Context manager that yields a database session.
        If a session was injected in __init__, it uses that one.
        Otherwise, it creates a new session using get_db_session().
        """
        if self._db_session:
            yield self._db_session
        else:
            with get_db_session() as db:
                yield db
