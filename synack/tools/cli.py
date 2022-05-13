from synack import synack
import cmd2
import sys

class SynackCLI(cmd2.Cmd):
    def __init__(self):
        self.prompt = "SYNACK> "
        super().__init__()
        self.s1 = synack()
        self.s1.gecko = False
        self.add_settable(cmd2.Settable('gecko', bool, 'Use Gecko instead of requests', self.s1))
        self.add_settable(cmd2.Settable('proxyport', int, 'Proxy port for requests', self.s1))
        self.add_settable(cmd2.Settable('Proxy', bool, 'Use proxy for requests', self.s1))
        self.s1.getSessionToken()
        
    def _get_all_targets(self):
        status_code = self.s1.getAllTargets()
        if status_code != 200:
            raise Exception("Invalid status code: %d" % status_code)
        
    def do_all_targets(self, args):
        """
        Get the list of all available targets
        """
        self._get_all_targets()
        for entry in self.s1.jsonResponse:
            print("    " + entry["codename"] + " (" + entry["category"]["name"] + "): " + entry["name"])
            
    codenames_parser = cmd2.Cmd2ArgumentParser()
    codenames_parser.add_argument('category', type=str, help='Target category (web, re, mobile, host, sourcecode, hardware)')
    codenames_parser.add_argument('-m', '--mission-only', action='store_true', help='Mission-only targets')

    @cmd2.with_argparser(codenames_parser)
    def do_codenames(self, args):
        """
        Get the list of all available target codenames within a category
        """
        self._get_all_targets()
        category = args.category
        codenames = self.s1.getCodenames(args.category, mission_only=args.mission_only)
        print("    " + "\n    ".join(codenames))
            
    target_id_parser = cmd2.Cmd2ArgumentParser()
    target_id_parser.add_argument('codename', type=str, help='Target codename')
    
    @cmd2.with_argparser(target_id_parser)
    def do_target_id(self, args):
        """
        Get the slug ID of a target from its codename
        """
        self._get_all_targets()
        print("    " + self.s1.getTargetID(args.codename))
        
    slug_parser = cmd2.Cmd2ArgumentParser()
    slug_parser.add_argument('slug', type=str, help='Target slug')
        
    @cmd2.with_argparser(slug_parser)
    def do_codename_from_slug(self, args):
        """
        Get the codename of a target from its slug ID
        """
        self._get_all_targets()
        print("    " + self.s1.getCodenameFromSlug(args.slug))
        
    category_parser = cmd2.Cmd2ArgumentParser()
    category_parser.add_argument('codename', type=str, help='Target codename')
            
    @cmd2.with_argparser(category_parser)
    def do_category(self, args):
        """
        Get the category of a target from its codename
        """
        self._get_all_targets()
        print("    " + self.s1.getCategory(args.codename))
        
    client_name_parser = cmd2.Cmd2ArgumentParser()
    client_name_parser.add_argument('codename', type=str, help='Target codename')
        
    @cmd2.with_argparser(client_name_parser)
    def do_client_name(self, args):
        """
        Get the client name of a target from its codename
        """
        self._get_all_targets()
        print("    " + self.s1.clientName(args.codename))
        
    connect_to_target_parser = cmd2.Cmd2ArgumentParser()
    connect_to_target_parser.add_argument('codename', type=str, help='Target codename')
        
    @cmd2.with_argparser(connect_to_target_parser)
    def do_connect_to_target(self, args):
        """
        Connect to a target by its codename
        """
        self._get_all_targets()
        print("    Status Code: %d" % self.s1.connectToTarget(args.codename))
        
    def do_disconnect_target(self, args):
        """
        Disconnect from the target
        """
        print("    Status Code: %d" % self.s1.disconnectTarget())
        
    scope_parser = cmd2.Cmd2ArgumentParser()
    scope_parser.add_argument('codename', type=str, help='Target codename')
        
    @cmd2.with_argparser(scope_parser)
    def do_scope(self, args):
        """
        Get the scope of a target by its codename
        """
        self._get_all_targets()
        #TODO: parse this to look pretty
        response = self.s1.getScope(args.codename)
        print(response)
        
    def do_assessments(self, args):
        """
        Get the list of your passed assessments
        """
        self.s1.getAssessments()
        print("    " + "\n    ".join(self.s1.assessments))
        
    analytics_parser = cmd2.Cmd2ArgumentParser()
    analytics_parser.add_argument('codename', type=str, help='Target codename')
    analytics_parser.add_argument('-s', '--status', type=str, default='all', help='Status (all, accepted, in_queue, rejected)')
        
    @cmd2.with_argparser(analytics_parser)
    def do_analytics(self, args):
        """
        Get the analytics from a target by its codename
        """
        self._get_all_targets()
        #TODO: parse this to look pretty
        response = self.s1.getAnalytics(args.codename, status=args.status)
        print(response)
        
    def do_register_all(self, args):
        """
        Register for all available targets
        """
        self.s1.registerAll()
        
    def do_keepalive(self, args):
        """
        Platform keepalive
        """
        self.s1.connectToPlatform()
        
    vulns_parser = cmd2.Cmd2ArgumentParser()
    vulns_parser.add_argument('-s', '--status', type=str, default='accepted', help='Status (accepted, rejected, ...)')
        
    @cmd2.with_argparser(vulns_parser)
    def do_vulns(self, args):
        """
        Get a list of your vulns
        """
        for vuln in self.s1.getVulns(status=args.status):
            vuln_info = "    [" + vuln["id"] + "] " + vuln["title"] + " (" + vuln["state"] + ")"
            if vuln.get("market_value_final") is not None:
                vuln_info += " $" + str(vuln["market_value_final"])
            print(vuln_info)
            
    vuln_parser = cmd2.Cmd2ArgumentParser()
    vuln_parser.add_argument('id', type=str, help='Vulnerability ID (e.g. optimusant-4)')

    @cmd2.with_argparser(vuln_parser)
    def do_vuln(self, args):
        """
        Get a vulnerability report
        """
        #TODO: parse this to look pretty
        print(self.s1.getVuln(args.id))
        
    def do_drafts(self, args):
        """
        Get a list of your draft vuln reports
        """
        for vuln in self.s1.getDrafts():
            print("    " + str(vuln["id"]) + " [" + vuln["listing"]["codename"] + "] " + vuln["vulnerability_blob"]["title"])
            
    draft_parser = cmd2.Cmd2ArgumentParser()
    draft_parser.add_argument('id', type=int, help='Draft ID')
    
    @cmd2.with_argparser(draft_parser)
    def do_delete_draft(self, args):
        """
        Delete a draft vulnerability report
        """
        if self.s1.deleteDraft(args.id):
            print("    Success!")
        else:
            print("    Failed to delete draft!")
            
    hydra_parser = cmd2.Cmd2ArgumentParser()
    hydra_parser.add_argument('codename', type=str, help='Target codename')
            
    @cmd2.with_argparser(hydra_parser)
    def do_hydra(self, args):
        """
        Get the hydra listings of a target by its codename
        """
        self._get_all_targets()
        #TODO: parse this to look pretty
        response = self.s1.getHydra(args.codename)
        print(response)
        
    def do_poll_missions(self, args):
        """
        Poll for available missions
        """
        #TODO: parse this to look pretty
        response = self.s1.pollMissions()
        print(response)
        
    claim_missions_parser = cmd2.Cmd2ArgumentParser()
    claim_missions_parser.add_argument('-d', '--dontclaim', type=str, default='', help='Don\'t claim missions on these targets, separated by commas')
    claim_missions_parser.add_argument('-a', '--asset', type=str, default='', help='Only claim asset type (web, re, mobile, host, sourcecode, hardware), separated by commas')
        
    @cmd2.with_argparser(claim_missions_parser)
    def do_claim_missions(self, args):
        """
        Claim available missions
        """
        response = self.s1.pollMissions()
        if len(response) == 0:
            print("    No missions available")
        else:
            missionList = self.s1.claimMissions(response, dontclaim=args.dontclaim.split(','), assetType=args.asset.split(','))
            for mission in missionList:
                print("    " + mission["target"] + " $" + str(mission["payout"]) + " claimed: " + str(mission["claimed"]))
                
    def do_notification_token(self, args):
        """
        Get the notification token
        """
        self.s1.getNotificationToken()
        print("    %s" % self.s1.notificationToken)

    def do_mark_notifications_read(self, args):
        """
        Mark notifications as read
        """
        if self.s1.markNotificationsRead() == 0:
            print("    Success!")
        else:
            print("    Failure!")
        
    def do_poll_notifications(self, args):
        """
        Poll for new notifications
        """
        for notification in self.s1.pollNotifications():
            print("    " + notification["created_at"] + " " + notification["action"] + " " + notification["subject"])
        
    def do_current_target(self, args):
        """
        Get the currently selected target
        """
        self._get_all_targets()
        slug = self.s1.getCurrentTargetSlug()
        if slug is None:
            print("    No target selected!")
        else:
            print("    " + self.s1.getCodenameFromSlug(slug))
            
    roes_parser = cmd2.Cmd2ArgumentParser()
    roes_parser.add_argument('codename', type=str, help='Target codename')
            
    @cmd2.with_argparser(roes_parser)
    def do_roes(self, args):
        """
        Get the ROEs of a target by its codename
        """
        self._get_all_targets()
        slug = self.s1.getTargetID(args.codename)
        #TODO: parse this to look pretty
        result = self.s1.getRoes(slug)
        print(result)
        
    def do_transactions(self, args):
        """
        Get the list of transactions
        """
        payouts = self.s1.getTransactions()
        for payout in payouts:
            print("    " + payout)    
        
if __name__ == '__main__':
    app = SynackCLI()
    sys.exit(app.cmdloop())
