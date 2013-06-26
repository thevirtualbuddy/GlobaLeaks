# -*- encoding: utf-8 -*-

from globaleaks import models
from storm.exceptions import OperationalError
from storm.locals import *
from globaleaks.settings import GLSetting


class TableReplacer:
    """
    This is the base class used by every Updater
    """

    def __init__(self, old_db_file, new_db_file, start_ver):

        self.old_db_file = old_db_file
        self.new_db_file = new_db_file
        self.start_ver = start_ver

        self.std_fancy = " + "
        self.debug_info = "   [%d => %d ]" %  (start_ver, start_ver + 1)

        print "%s Opening old version DB: %s" % (self.debug_info, old_db_file)
        old_database = create_database("sqlite:%s" % self.old_db_file)
        self.store_old = Store(old_database)

        GLSetting.db_file = new_db_file

        new_database = create_database("sqlite:%s" % new_db_file)
        self.store_new = Store(new_database)

        with open(GLSetting.db_schema_file) as f:
            create_queries = ''.join(f.readlines()).split(';')
            for create_query in create_queries:

                intermediate_sql = self.get_right_sql_version(create_query)
                if intermediate_sql:
                    create_query = intermediate_sql

                try:
                    self.store_new.execute(create_query+';')
                except OperationalError as excep:
                    print "%s OperationalError in [%s]" % (self.debug_info, create_query)
                    raise excep

        self.store_new.commit()

    def close(self):
        self.store_old.close()
        self.store_new.close()

    def initialize(self):
        pass

    def epilogue(self):
        pass

    ## ------------------------------------------------
    ## WARNING -this shit require almost a wiki page :D
    def get_right_model_version(self, table_name):
        """
        I'm sad of this piece of code, but having an ORM that need the
        intermediate version of the Models, bring this
        """
        if table_name == "Node" and self.start_ver == 0:
            from globaleaks.db.update_1_2 import Node_version_1
            return Node_version_1
        else:
            raise NotImplementedError

    ## ------------------------------------------------
    ## WARNING -this shit require almost a wiki page :D

    def get_right_sql_version(self, query):
        if query.startswith('\n\nCREATE TABLE node') and self.start_ver == 0:
            return 'CREATE TABLE node (database_version INTEGER NOT NULL,creation_date VARCHAR NOT NULL,'\
                'description VARCHAR NOT NULL,email VARCHAR NOT NULL,hidden_service VARCHAR NOT NULL,id VARCHAR NOT NULL,'\
                'languages BLOB NOT NULL, name VARCHAR NOT NULL, password VARCHAR NOT NULL, salt VARCHAR NOT NULL,'\
                'receipt_salt VARCHAR NOT NULL,public_site VARCHAR NOT NULL,stats_update_time INTEGER NOT NULL,'\
                'last_update VARCHAR,maximum_namesize INTEGER NOT NULL,maximum_descsize INTEGER NOT NULL,'\
                'maximum_textsize INTEGER NOT NULL,maximum_filesize INTEGER NOT NULL,tor2web_admin INTEGER NOT NULL,'\
                'tor2web_submission INTEGER NOT NULL,tor2web_tip INTEGER NOT NULL,tor2web_receiver INTEGER NOT NULL,'\
                'tor2web_unauth INTEGER NOT NULL,exception_email VARCHAR NOT NULL,PRIMARY KEY (id)\n)'
        return False
    ## ------------------------------------------------
    ## Here end the shit that require almost a wiki page


    def migrate_Context(self):
        print "%s default Context migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.Context).count())

        old_contexts = self.store_old.find(models.Context)

        for oc in old_contexts:

            new_obj = models.Context()
            new_obj.id = oc.id

            new_obj.creation_date = oc.creation_date
            new_obj.last_update = oc.last_update

            new_obj.name = oc.name
            new_obj.description = oc.description

            new_obj.file_required = oc.file_required
            new_obj.selectable_receiver = oc.selectable_receiver

            new_obj.tip_max_access = oc.tip_max_access
            new_obj.file_max_download = oc.file_max_download
            new_obj.file_required = oc.file_required
            new_obj.escalation_threshold = oc.escalation_threshold
            new_obj.tip_timetolive = oc.tip_timetolive
            new_obj.submission_timetolive = oc.submission_timetolive

            new_obj.receipt_regexp =  oc.receipt_regexp
            new_obj.receipt_description =  oc.receipt_description
            new_obj.submission_introduction = oc.submission_introduction
            new_obj.submission_disclaimer = oc.submission_disclaimer

            new_obj.fields = oc.fields
            new_obj.tags = oc.tags

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_Node(self):
        print "%s default Node migration assistant" % self.debug_info

        new_obj = self.get_right_model_version("Node")()
        on = self.store_old.find(self.get_right_model_version("Node")).one()

        new_obj.description = on.description
        new_obj.name = on.name
        new_obj.exception_email = on.exception_email
        new_obj.email = on.email

        new_obj.creation_date = on.creation_date
        new_obj.last_update = on.last_update

        new_obj.maximum_descsize = on.maximum_descsize
        new_obj.maximum_filesize = on.maximum_filesize
        new_obj.maximum_namesize = on.maximum_namesize
        new_obj.maximum_textsize = on.maximum_textsize

        new_obj.database_version = on.database_version

        new_obj.hidden_service = on.hidden_service
        new_obj.id = on.id

        new_obj.languages = on.languages
        new_obj.password = on.password
        new_obj.public_site = on.public_site
        new_obj.receipt_salt = on.receipt_salt
        new_obj.salt = on.salt
        new_obj.stats_update_time = on.stats_update_time

        new_obj.tor2web_admin = on.tor2web_admin
        new_obj.tor2web_receiver = on.tor2web_receiver
        new_obj.tor2web_submission = on.tor2web_submission
        new_obj.tor2web_tip = on.tor2web_tip
        new_obj.tor2web_unauth = on.tor2web_unauth

        self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_ReceiverTip(self):
        print "%s default ReceiverTip migration assistant: #%d" % (
              self.debug_info, self.store_old.find(models.ReceiverTip).count() )

        old_receivertips = self.store_old.find(models.ReceiverTip)

        for ort in old_receivertips:

            new_obj = models.ReceiverTip()

            new_obj.id = ort.id
            new_obj.internaltip_id = ort.internaltip_id
            new_obj.receiver_id = ort.receiver_id

            new_obj.expressed_pertinence = ort.expressed_pertinence
            new_obj.last_access = ort.last_access
            new_obj.access_counter = ort.access_counter
            new_obj.mark = ort.mark
            new_obj.notification_date = ort.notification_date

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_WhistleblowerTip(self):
        print "%s default WhistleblowerTip migration assistant: #%d" % (
              self.debug_info, self.store_old.find(models.WhistleblowerTip).count())

        old_wbtips = self.store_old.find(models.WhistleblowerTip)

        for owbt in old_wbtips:

            new_obj = models.WhistleblowerTip()

            new_obj.id = owbt.id

            new_obj.creation_date = owbt.creation_date
            new_obj.last_access = owbt.last_access

            new_obj.access_counter = owbt.access_counter
            new_obj.internaltip_id = owbt.internaltip_id

            new_obj.receipt_hash = owbt.receipt_hash

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_Comment(self):
        print "%s default Comments migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.Comment).count())

        old_comments = self.store_old.find(models.Comment)

        for oc in old_comments:

            new_obj = models.Comment()

            new_obj.author = oc.author
            new_obj.content = oc.content
            new_obj.creation_date = oc.creation_date
            new_obj.id = oc.id
            new_obj.internaltip_id = oc.internaltip_id
            new_obj.mark = oc.mark
            new_obj.type = oc.type

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_InternalTip(self):
        print "%s default InternalTips migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.InternalTip).count())

        old_itips = self.store_old.find(models.InternalTip)

        for oit in old_itips:

            new_obj = models.InternalTip()

            new_obj.id = oit.id
            new_obj.context_id = oit.context_id

            new_obj.wb_fields = oit.wb_fields

            new_obj.expiration_date = oit.expiration_date
            new_obj.creation_date = oit.creation_date
            new_obj.last_activity = oit.last_activity

            new_obj.access_limit = oit.access_limit
            new_obj.download_limit = oit.download_limit
            new_obj.escalation_threshold = oit.escalation_threshold
            new_obj.mark = oit.mark
            new_obj.pertinence_counter = oit.pertinence_counter

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_Receiver(self):
        print "%s default Receivers migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.Receiver).count())

        old_receivers = self.store_old.find(models.Receiver)

        for orcvr in old_receivers:

            new_obj = models.Receiver()

            new_obj.username = orcvr.username
            new_obj.id = orcvr.id
            new_obj.name = orcvr.name
            new_obj.password = orcvr.password
            new_obj.description = orcvr.description

            new_obj.can_delete_submission = orcvr.can_delete_submission
            new_obj.comment_notification = orcvr.comment_notification
            new_obj.tip_notification = orcvr.tip_notification
            new_obj.file_notification = orcvr.file_notification

            new_obj.creation_date = orcvr.creation_date
            new_obj.last_access = orcvr.last_access
            new_obj.last_update = orcvr.last_update

            new_obj.failed_login = orcvr.failed_login

            new_obj.gpg_key_armor = orcvr.gpg_key_armor
            new_obj.gpg_key_fingerprint = orcvr.gpg_key_fingerprint
            new_obj.gpg_key_info = orcvr.gpg_key_info
            new_obj.gpg_key_status = orcvr.gpg_key_status

            new_obj.receiver_level = orcvr.receiver_level

            new_obj.notification_fields = orcvr.notification_fields
            new_obj.tags = orcvr.tags

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_InternalFile(self):
        print "%s default InternalFiles migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.InternalFile).count() )

        old_internalfiles = self.store_old.find(models.InternalFile)

        for oi in old_internalfiles:

            new_obj = models.InternalFile()

            new_obj.id = oi.id
            new_obj.name = oi.name
            new_obj.content_type = oi.content_type
            new_obj.sha2sum = oi.sha2sum

            new_obj.creation_date = oi.creation_date
            new_obj.file_path = oi.file_path
            new_obj.internaltip_id = oi.internaltip_id
            new_obj.mark = oi.mark
            new_obj.size = oi.size

            self.store_old.add(new_obj)
        self.store_new.commit()

    def migrate_ReceiverFile(self):
        print "%s default ReceiverFile migration assistant: #%d" % (
            self.debug_info, self.store_old.find(models.ReceiverFile).count() )

        old_receiverfiles = self.store_old.find(models.ReceiverFile)

        for orf in old_receiverfiles:

            new_obj = models.ReceiverFile()

            new_obj.id = orf.id
            new_obj.internalfile_id = orf.internalfile_id
            new_obj.internaltip_id = orf.internaltip_id
            new_obj.receiver_id = orf.receiver_id

            new_obj.creation_date = orf.creation_date
            new_obj.last_access = orf.last_access

            new_obj.downloads = orf.downloads
            new_obj.file_path = orf.file_path
            new_obj.mark = orf.mark

            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_Notification(self):
        print "%s default Notificationb migration assistant" % self.debug_info

        on = self.store_old.find(models.Notification).one()

        new_obj = models.Notification()

        new_obj.id = on.id

        new_obj.creation_date = on.creation_date
        new_obj.password = on.password
        new_obj.port = on.port
        new_obj.security = on.security
        new_obj.server = on.server
        new_obj.username = on.username

        new_obj.comment_mail_title = on.comment_mail_title
        new_obj.comment_template = on.comment_template
        new_obj.file_mail_title = on.file_mail_title
        new_obj.file_template = on.file_template
        new_obj.tip_mail_title = on.tip_mail_title
        new_obj.tip_template = on.tip_template

        self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_ReceiverContext(self):
        print "%s Migrate ReceiverContext reference tables: #%d" % (
            self.debug_info, self.store_old.find(models.ReceiverContext).count() )

        rc_relship = self.store_old.find(models.ReceiverContext)

        for rc in rc_relship:
            new_obj = models.ReceiverContext()
            new_obj.context_id = rc.context_id
            new_obj.receiver_id = rc.receiver_id
            self.store_new.add(new_obj)
        self.store_new.commit()

    def migrate_ReceiverInternalTip(self):
        print "%s Migrate ReceiverInternalTip reference tables: #%d" % (
            self.debug_info, self.store_old.find(models.ReceiverInternalTip).count() )

        ri_relship = self.store_old.find(models.ReceiverInternalTip)

        for ri in ri_relship:
            new_obj = models.ReceiverInternalTip()
            new_obj.internaltip_id = ri.internaltip_id
            new_obj.receiver_id = ri.receiver_id
            self.store_new.add(new_obj)
        self.store_new.commit()

