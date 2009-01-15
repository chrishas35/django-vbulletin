import logging
import md5

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from vbulletin.auth import VBULLETIN_CONFIG

class VBulletinBackend(ModelBackend):
    """
    We override ModelBackend to make use of django.contrib.auth permissions
    """
    
    def authenticate(self, username=None, password=None):
        logging.debug('Using VBulletinBackend')
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""SELECT userid, username, password, salt, usergroupid, membergroupids
                          FROM %suser WHERE username = '%s'"""
                       % (VBULLETIN_CONFIG['tableprefix'], username))
        row = cursor.fetchone()
        
        hashed = md5.new(md5.new(password).hexdigest() + row[3]).hexdigest()
        
        if row[2] == hashed:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                
                user.is_staff = False
                user.is_superuser = False

                # Process primary usergroup
                if row[4] in VBULLETIN_CONFIG['superuser_groupids']:
                    user.is_staff = True    
                    user.is_superuser = True
                elif row[4] in VBULLETIN_CONFIG['staff_groupids']:
                    user.is_staff = True
                
                # Process addtional usergroups
                for groupid in row[5].split(','):
                    if groupid in VBULLETIN_CONFIG['superuser_groupids']:
                        user.is_superuser = True
                    if groupid in VBULLETIN_CONFIG['staff_groupids']:
                        user.is_staff = True
                
                user.set_unusable_password()
                user.save()
            return user
            
        return None