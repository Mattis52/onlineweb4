# -*- coding: utf-8 -*-
import ldapdb.models
import passlib
import time

from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
from onlineweb4.settings.local import LDAP_BASE_DN, SAMBA_SID_BASE
from passlib.hash import ldap_sha512_crypt, nthash, lmhash


class LdapOrgUnit(ldapdb.models.Model):
    """
    Class for representing an LDAP organizational unit entry
    """
    base_dn = LDAP_BASE_DN
    object_classes = ['organizationalUnit']

    name = CharField(db_column='ou', primary_key=True, unique=True)

    def __str__(self):
        return self.name


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou=people," + LDAP_BASE_DN
    object_classes = ['posixAccount', 'shadowAccount', 'inetOrgPerson']

    # inetOrgPerson
    first_name = CharField(db_column='givenName')
    last_name = CharField(db_column='sn')
    full_name = CharField(db_column='cn', blank=True)
    email = CharField(db_column='mail', blank=True)
    phone = CharField(db_column='telephoneNumber', blank=True)
    mobile_phone = CharField(db_column='mobile', blank=True)
    photo = ImageField(db_column='jpegPhoto', blank=True)

    # posixAccount
    uid = IntegerField(db_column='uidNumber', unique=True)
    group = IntegerField(db_column='gidNumber')
    gecos = CharField(db_column='gecos', blank=True)
    home_directory = CharField(db_column='homeDirectory', blank=True)
    login_shell = CharField(db_column='loginShell', default='/bin/false')
    username = CharField(db_column='uid', primary_key=True, unique=True)
    password = CharField(db_column='userPassword', blank=True)

    # sambaAccount
    samba_sid = CharField(db_column='sambaSID')
    samba_flags = CharField(db_column='sambaAcctFlags')
    samba_pwd_last_set = CharField(db_column='sambaPwdLastSet')
    samba_pwd_must_change = CharField(db_column='sambaPwdMustChange')
    ntpassword = CharField(db_column='sambaNTPassword')
    lmpassword = CharField(db_column='sambaLMPassword')

    def __str__(self):
        return self.username

    def set_password(self, password):
        self.password = ldap_sha512_crypt.encrypt(password)
        self.save()

    def enable_shell(self, shell='/bin/bash'):
        self.login_shell = shell

    def enable_samba_account(self, password):
        self.samba_sid = SAMBA_SID_BASE + str((self.uid * 2) + 1000)
        self.samba_pwd_last_set = str(int(time.time()))
        self.samba_pwd_must_change = '2524608000' # year 2050
        self.samba_flags = '[U]'
        self.ntpassword = nthash.encrypt(password).upper()
        self.lmpassword = lmhash.encrypt(password).upper()
        self.save()

    def check_password(self, password):
        return ldap_sha512_crypt.verify(password, self.password)


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=groups," + LDAP_BASE_DN
    object_classes = ['posixGroup']

    # posixGroup attributes
    gid = IntegerField(db_column='gidNumber', unique=True, blank=True)
    name = CharField(db_column='cn', max_length=200, primary_key=True)
    usernames = ListField(db_column='memberUid', blank=True)

    def __str__(self):
        return self.name
