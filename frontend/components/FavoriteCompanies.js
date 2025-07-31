import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Button,
  Linking,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  Image,
  RefreshControl,
  TextInput
} from 'react-native';
import { useUser } from '../context/UserContext';
import { API_URL } from '../config';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

// Map of company names to logo URLs (deduplicated, standardized, US/Canada focus)
const COMPANY_LOGOS = {
  'Retool': 'https://logo.clearbit.com/retool.com',
  'Nextdoor': 'https://logo.clearbit.com/nextdoor.com',
  'Duolingo': 'https://logo.clearbit.com/duolingo.com',
  'Viral Nation': 'https://logo.clearbit.com/viralnation.com',
  'Bond Brand Loyalty': 'https://logo.clearbit.com/bondbrandloyalty.com',
  'StackAdapt': 'https://logo.clearbit.com/stackadapt.com',
  'Index Exchange': 'https://logo.clearbit.com/indexexchange.com',
  'OpenText': 'https://logo.clearbit.com/opentext.com',
  'Barnacle Systems Inc.': 'https://logo.clearbit.com/barnacle.io',
  'Chime': 'https://logo.clearbit.com/chime.com',
  'Boosted.ai': 'https://logo.clearbit.com/boosted.ai',
  'Coda': 'https://logo.clearbit.com/coda.io',
  'Top Hat': 'https://logo.clearbit.com/tophat.com',
  'Hightouch': 'https://logo.clearbit.com/hightouch.com',
  'Intelliculture': 'https://logo.clearbit.com/intelliculture.com',
  'OpsLevel': 'https://logo.clearbit.com/opslevel.com',
  'Otter.ai': 'https://logo.clearbit.com/otter.ai',
  'CircleCI': 'https://logo.clearbit.com/circleci.com',
  'Flywheel Digital': 'https://logo.clearbit.com/flywheeldigital.com',
  'NURO': 'https://logo.clearbit.com/nuro.ai',
  'Trellis': 'https://logo.clearbit.com/trellis.org',
  'Retailogists': '', // No clearbit logo
  'Adaptivist': 'https://logo.clearbit.com/adaptavist.com',
  'Ledn': 'https://logo.clearbit.com/ledn.io',
  'RouteThis': 'https://logo.clearbit.com/routethis.com',
  'BIMM': 'https://logo.clearbit.com/bimm.com',
  'Ziphq': 'https://logo.clearbit.com/ziphq.com',
  'Wish': 'https://logo.clearbit.com/wish.com',
  'SkipTheDishes': 'https://logo.clearbit.com/skipthedishes.com',
  'TouchBistro': 'https://logo.clearbit.com/touchbistro.com',
  'Thoughtworks': 'https://logo.clearbit.com/thoughtworks.com',
  'Etsy': 'https://logo.clearbit.com/etsy.com',
  'Cloudflare': 'https://logo.clearbit.com/cloudflare.com',
  'Chainalysis': 'https://logo.clearbit.com/chainalysis.com',
  'Binance': 'https://logo.clearbit.com/binance.com',
  'Webtoon Entertainment': 'https://logo.clearbit.com/webtoons.com',
  'Wave': 'https://logo.clearbit.com/waveapps.com',
  'Rogers': 'https://logo.clearbit.com/rogers.com',
  'Loop Financial': '', // No clearbit logo
  'Prodigy Education': 'https://logo.clearbit.com/prodigygame.com',
  'Clearco': 'https://logo.clearbit.com/clear.co',
  'Archon Systems Inc.': 'https://logo.clearbit.com/archonsystems.com',
  'Plenty of Fish': 'https://logo.clearbit.com/pof.com',
  'Venngage': 'https://logo.clearbit.com/venngage.com',
  'Ritual.co': 'https://logo.clearbit.com/ritual.co',
  'Swoon': 'https://logo.clearbit.com/swoonstaffing.com',
  'Zillow': 'https://logo.clearbit.com/zillow.com',
  'Coinbase': 'https://logo.clearbit.com/coinbase.com',
  'Wayfair': 'https://logo.clearbit.com/wayfair.com',
  'Okta': 'https://logo.clearbit.com/okta.com',
  'Faire': 'https://logo.clearbit.com/faire.com',
  'Instacart': 'https://logo.clearbit.com/instacart.com',
  'Stripe': 'https://logo.clearbit.com/stripe.com',
  'Reddit': 'https://logo.clearbit.com/reddit.com',
  'Airbnb': 'https://logo.clearbit.com/airbnb.com',
  'Uber': 'https://logo.clearbit.com/uber.com',
  'Bluedot': 'https://logo.clearbit.com/bluedot.io',
  'Rippling': 'https://logo.clearbit.com/rippling.com',
  'Cohere': 'https://logo.clearbit.com/cohere.com',
  'Clutch': 'https://logo.clearbit.com/clutch.com',
  'Dapper Labs': 'https://logo.clearbit.com/dapperlabs.com',
  'Outschool': 'https://logo.clearbit.com/outschool.com',
  'Bolt': 'https://logo.clearbit.com/bolt.com',
  'Upgrade': 'https://logo.clearbit.com/upgrade.com',
  'Lyft': 'https://logo.clearbit.com/lyft.com',
  'Lookout': 'https://logo.clearbit.com/lookout.com',
  'ApplyBoard': 'https://logo.clearbit.com/applyboard.com',
  'Dialpad': 'https://logo.clearbit.com/dialpad.com',
  'Addepar': 'https://logo.clearbit.com/addepar.com',
  'Hopper': 'https://logo.clearbit.com/hopper.com',
  'Notch': 'https://logo.clearbit.com/notch.com',
  'VTS': 'https://logo.clearbit.com/vts.com',
  'Cockroach Labs': 'https://logo.clearbit.com/cockroachlabs.com',
  'Hyperscience': 'https://logo.clearbit.com/hyperscience.com',
  'Rivian': 'https://logo.clearbit.com/rivian.com',
  'ChargePoint': 'https://logo.clearbit.com/chargepoint.com',
  'LinkedIn': 'https://logo.clearbit.com/linkedin.com',
  'Tonal': 'https://logo.clearbit.com/tonal.com',
  'GlossGenius': 'https://logo.clearbit.com/glossgenius.com',
  'Square': 'https://logo.clearbit.com/squareup.com',
  'Unether AI': '', // No clearbit logo
  'Copado': 'https://logo.clearbit.com/copado.com',
  'EvenUp': 'https://logo.clearbit.com/evenup.com',
  'Super.com': 'https://logo.clearbit.com/super.com',
  'BenchSci': 'https://logo.clearbit.com/benchsci.com',
  'Benevity': 'https://logo.clearbit.com/benevity.com',
  'Vena Solutions': 'https://logo.clearbit.com/venasolutions.com',
  'Vagaro': 'https://logo.clearbit.com/vagaro.com',
  'Fabric.inc': 'https://logo.clearbit.com/fabric.inc',
  'Procurify': 'https://logo.clearbit.com/procurify.com',
  'App Annie': 'https://logo.clearbit.com/data.ai',
  'Tenstorrent': 'https://logo.clearbit.com/tenstorrent.com',
  'Forethought': 'https://logo.clearbit.com/forethought.ai',
  'Course Hero': 'https://logo.clearbit.com/coursehero.com',
  'League': 'https://logo.clearbit.com/league.com',
  'Chegg': 'https://logo.clearbit.com/chegg.com',
  'AI Redefined': 'https://logo.clearbit.com/ai-r.com',
  'Mistplay': 'https://logo.clearbit.com/mistplay.com',
  'Moves Financial': 'https://logo.clearbit.com/movesfinancial.com',
  'Grammarly': 'https://logo.clearbit.com/grammarly.com',
  'Replit': 'https://logo.clearbit.com/replit.com',
  'Replicant': 'https://logo.clearbit.com/replicant.ai',
  'Plooto': 'https://logo.clearbit.com/plooto.com',
  'Fullscript': 'https://logo.clearbit.com/fullscript.com',
  'Rose Rocket': 'https://logo.clearbit.com/roserocket.com',
  'Validere': 'https://logo.clearbit.com/validere.com',
  'Certn': 'https://logo.clearbit.com/certn.co',
  'Coffee Meets Bagel': 'https://logo.clearbit.com/coffeemeetsbagel.com',
  'Mattermost': 'https://logo.clearbit.com/mattermost.com',
  'AuditBoard': 'https://logo.clearbit.com/auditboard.com',
  'Studio': '', // No clearbit logo
  'Pachyderm': 'https://logo.clearbit.com/pachyderm.com',
  'Sanctuary AI': 'https://logo.clearbit.com/sanctuary.ai',
  'Platter': '', // No clearbit logo
  'Unity': 'https://logo.clearbit.com/unity.com',
  'GoDaddy': 'https://logo.clearbit.com/godaddy.com',
  'CentralSquare Technologies': 'https://logo.clearbit.com/centralsquare.com',
  'Yelp': 'https://logo.clearbit.com/yelp.com',
  'NODA': '', // No clearbit logo
  'CentML': 'https://logo.clearbit.com/centml.ai',
  'Remarcable Inc.': '', // No clearbit logo
  'SAGE': 'https://logo.clearbit.com/sage.com',
  'X': 'https://logo.clearbit.com/x.com',
  'Tesla': 'https://logo.clearbit.com/tesla.com',
  'TMX Group': 'https://logo.clearbit.com/tmx.com',
  'Nvidia': 'https://logo.clearbit.com/nvidia.com',
  'Arctic Wolf': 'https://logo.clearbit.com/arcticwolf.com',
  'Nokia': 'https://logo.clearbit.com/nokia.com',
  'AMD': 'https://logo.clearbit.com/amd.com',
  'Vopemed': '', // No clearbit logo
  'Flashfood': 'https://logo.clearbit.com/flashfood.com',
  'Gusto': 'https://logo.clearbit.com/gusto.com',
  'Epic Games': 'https://logo.clearbit.com/epicgames.com',
  'Cribl': 'https://logo.clearbit.com/cribl.io',
  'Slack': 'https://logo.clearbit.com/slack.com',
  'Indigo': 'https://logo.clearbit.com/indigo.ca',
  'Auvik Networks': 'https://logo.clearbit.com/auvik.com',
  'SOTI': 'https://logo.clearbit.com/soti.net',
  'KeyDataCyber': 'https://logo.clearbit.com/keydatacyber.com',
  'Opifiny Corp': 'https://logo.clearbit.com/opifiny.com',
  'Meta': 'https://logo.clearbit.com/meta.com',
  'Bitsight': 'https://logo.clearbit.com/bitsight.com',
  'Spotify': 'https://logo.clearbit.com/spotify.com',
  'Electronic Arts': 'https://logo.clearbit.com/ea.com',
  'Workiva': 'https://logo.clearbit.com/workiva.com',
  'The Trade Desk': 'https://logo.clearbit.com/thetradedesk.com',
  'Robinhood': 'https://logo.clearbit.com/robinhood.com',
  'Intelliware': 'https://logo.clearbit.com/intelliware.com',
  'Figma': 'https://logo.clearbit.com/figma.com',
  'Verkada': 'https://logo.clearbit.com/verkada.com',
  'Schonfeld': 'https://logo.clearbit.com/schonfeld.com',
  'Ecomtent': '', // No clearbit logo
  'Citrus (Camp Management Software)': '', // No clearbit logo
  'TalentMinded': 'https://logo.clearbit.com/talentminded.ca',
  'Transify': '', // No clearbit logo
  'Sync.com': 'https://logo.clearbit.com/sync.com',
  'Questrade': 'https://logo.clearbit.com/questrade.com',
  'Xanadu': 'https://logo.clearbit.com/xanadu.ai',
  'Haft2 Inc.': '', // No clearbit logo
  'Demonware': 'https://logo.clearbit.com/demonware.net',
  'Shyft Labs': 'https://logo.clearbit.com/shyftlabs.io',
  'Wealthsimple': 'https://logo.clearbit.com/wealthsimple.com',
  'Infor': 'https://logo.clearbit.com/infor.com',
  'Connor, Clark & Lunn Infrastructure': 'https://logo.clearbit.com/cclinfrastructure.com',
  'FGS Global': 'https://logo.clearbit.com/fgsglobal.com',
  'Lancey': '', // No clearbit logo
  'Google': 'https://logo.clearbit.com/google.com',
  'Amazon': 'https://logo.clearbit.com/amazon.com',
  'Netflix': 'https://logo.clearbit.com/netflix.com',
  'Snapchat': 'https://logo.clearbit.com/snapchat.com',
  'Twilio': 'https://logo.clearbit.com/twilio.com',
};

// List of deduplicated, standardized company names
const COMPANIES = Object.keys(COMPANY_LOGOS);

// Map of company names to career page URLs (US/Canada focus, best match)
const COMPANY_CAREER_PAGES = {
  'Retool': 'https://retool.com/careers',
  'Nextdoor': 'https://about.nextdoor.com/careers/',
  'Duolingo': 'https://careers.duolingo.com/',
  'Viral Nation': 'https://www.viralnation.com/careers/',
  'Bond Brand Loyalty': 'https://www.bondbrandloyalty.com/about/careers/',
  'StackAdapt': 'https://www.stackadapt.com/careers',
  'Index Exchange': 'https://www.indexexchange.com/careers/',
  'OpenText': 'https://careers.opentext.com/',
  'Barnacle Systems Inc.': 'https://www.barnacle.io/pages/careers',
  'Chime': 'https://www.chime.com/careers/',
  'Boosted.ai': 'https://boosted.ai/careers/',
  'Coda': 'https://coda.io/careers',
  'Top Hat': 'https://tophat.com/company/careers/',
  'Hightouch': 'https://hightouch.com/careers',
  'Intelliculture': 'https://intelliculture.com/careers',
  'OpsLevel': 'https://www.opslevel.com/careers',
  'Otter.ai': 'https://otter.ai/careers',
  'CircleCI': 'https://circleci.com/careers',
  'Flywheel Digital': 'https://flywheeldigital.com/careers',
  'NURO': 'https://nuro.ai/careers',
  'Trellis': 'https://www.trellis.org/careers',
  'Retailogists': 'https://www.retailogists.com/careers',
  'Adaptivist': 'https://www.adaptavist.com/careers',
  'Ledn': 'https://ledn.io/careers',
  'RouteThis': 'https://routethis.com/careers',
  'BIMM': 'https://www.bimm.com/careers',
  'Ziphq': 'https://ziphq.com/careers',
  'Wish': 'https://www.wish.com/careers',
  'SkipTheDishes': 'https://www.skipthedishes.com/about/careers',
  'TouchBistro': 'https://www.touchbistro.com/careers/',
  'Thoughtworks': 'https://www.thoughtworks.com/careers',
  'Etsy': 'https://www.etsy.com/careers',
  'Cloudflare': 'https://www.cloudflare.com/careers/',
  'Chainalysis': 'https://www.chainalysis.com/careers/',
  'Binance': 'https://www.binance.com/en/careers',
  'Webtoon Entertainment': 'https://careers.webtoons.com/',
  'Wave': 'https://www.waveapps.com/careers',
  'Rogers': 'https://jobs.rogers.com/',
  'Loop Financial': 'https://www.bankonloop.com/en-ca/careers',
  'Prodigy Education': 'https://www.prodigygame.com/main-en/careers/',
  'Clearco': 'https://clear.co/careers',
  'Archon Systems Inc.': 'https://www.archonsystems.com/careers',
  'Plenty of Fish': 'https://www.pof.com/careers',
  'Venngage': 'https://venngage.com/careers',
  'Ritual.co': 'https://ritual.co/careers',
  'Swoon': 'https://swoonstaffing.com/careers/',
  'Zillow': 'https://www.zillowgroup.com/careers/',
  'Coinbase': 'https://www.coinbase.com/careers',
  'Wayfair': 'https://www.aboutwayfair.com/careers',
  'Okta': 'https://www.okta.com/company/careers/',
  'Faire': 'https://www.faire.com/careers',
  'Instacart': 'https://careers.instacart.com/',
  'Stripe': 'https://stripe.com/jobs',
  'Reddit': 'https://www.redditinc.com/careers',
  'Airbnb': 'https://careers.airbnb.com/',
  'Uber': 'https://www.uber.com/careers/',
  'Bluedot': 'https://bluedot.io/careers',
  'Rippling': 'https://www.rippling.com/careers',
  'Cohere': 'https://cohere.com/careers',
  'Clutch': 'https://clutch.com/careers',
  'Dapper Labs': 'https://www.dapperlabs.com/careers',
  'Outschool': 'https://outschool.com/careers',
  'Bolt': 'https://www.bolt.com/careers',
  'Upgrade': 'https://www.upgrade.com/careers',
  'Lyft': 'https://www.lyft.com/careers',
  'Lookout': 'https://www.lookout.com/company/careers',
  'ApplyBoard': 'https://www.applyboard.com/careers',
  'Dialpad': 'https://www.dialpad.com/careers',
  'Addepar': 'https://addepar.com/careers',
  'Hopper': 'https://www.hopper.com/careers',
  'Notch': 'https://notch.com/careers',
  'VTS': 'https://www.vts.com/careers',
  'Cockroach Labs': 'https://www.cockroachlabs.com/careers/',
  'Hyperscience': 'https://www.hyperscience.com/careers/',
  'Rivian': 'https://rivian.com/careers',
  'ChargePoint': 'https://www.chargepoint.com/about/careers',
  'LinkedIn': 'https://careers.linkedin.com/',
  'Tonal': 'https://www.tonal.com/careers',
  'GlossGenius': 'https://glossgenius.com/careers',
  'Square': 'https://squareup.com/us/en/careers',
  'Unether AI': '', // No official page found
  'Copado': 'https://www.copado.com/company/careers',
  'EvenUp': 'https://evenup.com/careers',
  'Super.com': 'https://super.com/careers',
  'BenchSci': 'https://www.benchsci.com/careers',
  'Benevity': 'https://benevity.com/careers',
  'Vena Solutions': 'https://www.venasolutions.com/careers',
  'Vagaro': 'https://www.vagaro.com/careers',
  'Fabric.inc': 'https://fabric.inc/careers',
  'Procurify': 'https://www.procurify.com/careers',
  'App Annie': 'https://www.data.ai/en/company/careers/',
  'Tenstorrent': 'https://www.tenstorrent.com/careers',
  'Forethought': 'https://forethought.ai/careers',
  'Course Hero': 'https://www.coursehero.com/jobs/',
  'League': 'https://league.com/careers',
  'Chegg': 'https://www.chegg.com/about/working-at-chegg',
  'AI Redefined': 'https://ai-r.com/careers',
  'Mistplay': 'https://www.mistplay.com/careers',
  'Moves Financial': 'https://www.movesfinancial.com/careers',
  'Grammarly': 'https://www.grammarly.com/jobs',
  'Replit': 'https://replit.com/careers',
  'Replicant': 'https://www.replicant.ai/careers',
  'Plooto': 'https://www.plooto.com/careers',
  'Fullscript': 'https://fullscript.com/careers',
  'Rose Rocket': 'https://www.roserocket.com/careers',
  'Validere': 'https://validere.com/careers',
  'Certn': 'https://certn.co/careers',
  'Coffee Meets Bagel': 'https://coffeemeetsbagel.com/careers',
  'Mattermost': 'https://mattermost.com/careers/',
  'AuditBoard': 'https://www.auditboard.com/company/careers/',
  'Pachyderm': 'https://www.pachyderm.com/careers',
  'Sanctuary AI': 'https://www.sanctuary.ai/careers',
  'Unity': 'https://careers.unity.com/',
  'GoDaddy': 'https://careers.godaddy.com/',
  'CentralSquare Technologies': 'https://www.centralsquare.com/about/careers',
  'Yelp': 'https://www.yelp.careers/us/en',
  'CentML': 'https://centml.ai/careers',
  'Remarcable Inc.': 'https://remarcable-inc.careerplug.com/jobs',
  'SAGE': 'https://www.sage.com/en-gb/company/careers/',
  'X': 'https://x.com/careers',
  'Tesla': 'https://www.tesla.com/careers',
  'TMX Group': 'https://www.tmx.com/about/careers',
  'Nvidia': 'https://www.nvidia.com/en-us/about-nvidia/careers/',
  'Arctic Wolf': 'https://arcticwolf.com/company/careers/',
  'Nokia': 'https://www.nokia.com/about-us/careers/',
  'AMD': 'https://www.amd.com/en/corporate/careers',
  'Flashfood': 'https://www.flashfood.com/careers',
  'Gusto': 'https://gusto.com/about/careers',
  'Epic Games': 'https://www.epicgames.com/site/en-US/careers',
  'Cribl': 'https://cribl.io/company/careers/',
  'Slack': 'https://slack.com/careers',
  'Indigo': 'https://careers.indigo.ca/',
  'Auvik Networks': 'https://www.auvik.com/about-us/careers/',
  'SOTI': 'https://www.soti.net/careers/',
  'KeyDataCyber': 'https://keydatacyber.com/careers',
  'Opifiny Corp': 'https://opifiny.com/careers',
  'Meta': 'https://www.metacareers.com/',
  'Tomato Pay Inc': 'https://apply.workable.com/tomato-pay/?lng=en', // No official page found
  'Bitsight': 'https://www.bitsight.com/company/careers',
  'Spotify': 'https://www.spotifyjobs.com/',
  'Electronic Arts': 'https://jobs.ea.com/en_US/careers/Home/Toronto?listFilterMode=1',
  'Workiva': 'https://www.workiva.com/careers',
  'The Trade Desk': 'https://www.thetradedesk.com/careers',
  'Robinhood': 'https://careers.robinhood.com/',
  'Intelliware': 'https://www.intelliware.com/careers/',
  'Figma': 'https://www.figma.com/careers/',
  'Verkada': 'https://www.verkada.com/careers/',
  'Schonfeld': 'https://www.schonfeld.com/careers',
  'Ecomtent': 'https://ecomtent.zohorecruit.ca/jobs/Careers',
  'Citrus (Camp Management Software)': 'https://www.joincitrus.com/join-our-team',
  'TalentMinded': 'https://www.talentminded.ca/careers',
  'Transify': 'https://www.transify.com/careers',
  'Sync.com': 'https://www.sync.com/careers',
  'Questrade': 'https://www.questrade.com/careers',
  'Xanadu': 'https://www.xanadu.ai/careers',
  'Demonware': 'https://demonware.net/careers',
  'Shyft Labs': 'https://shyftlabs.io/careers',
  'Wealthsimple': 'https://www.wealthsimple.com/en-ca/careers',
  'Infor': 'https://www.infor.com/about/careers',
  'Connor, Clark & Lunn Infrastructure': 'https://cclinfrastructure.com/careers',
  'FGS Global': 'https://fgsglobal.com/careers',
  'Lancey': 'https://www.ycombinator.com/companies/lancey/jobs',
  'Google': 'https://careers.google.com/jobs/',
  'Amazon': 'https://www.amazon.jobs/',
  'Netflix': 'https://jobs.netflix.com/',
  'Snapchat': 'https://snap.com/en-US/jobs',
  'Twilio': 'https://www.twilio.com/company/jobs',
};

// Helper to check if a job was posted today
function isJobPostedToday(job) {
  if (!job.posted_at) return false;
  const postedDate = new Date(job.posted_at);
  const now = new Date();
  return (
    postedDate.getFullYear() === now.getFullYear() &&
    postedDate.getMonth() === now.getMonth() &&
    postedDate.getDate() === now.getDate()
  );
}

const FavoriteCompanies = ({ onApply }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [applying, setApplying] = useState({});
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(true);
  const [totalCompanies, setTotalCompanies] = useState(0);
  const { user } = useUser();

  useEffect(() => {
    fetchJobs();
  }, [currentPage]);

  const fetchJobs = async (page = 1) => {
    setRefreshing(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/linked-companies-jobs?page=${page}&per_page=20`);
      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }
      const data = await response.json();

      if (page === 1) {
        // First page - replace data
        setJobs(data.companies || []);
      } else {
        // Subsequent pages - append data
        setJobs(prevJobs => [...prevJobs, ...(data.companies || [])]);
      }

      // Update pagination info
      setHasNextPage(data.pagination?.has_next || false);
      setTotalCompanies(data.pagination?.total_companies || 0);

    } catch (error) {
      console.error('Error fetching favorite jobs:', error);
      setError(`Failed to load jobs: ${error.message}`);
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  const loadMoreCompanies = () => {
    if (hasNextPage && !loading) {
      const nextPage = currentPage + 1;
      setCurrentPage(nextPage);
      fetchJobs(nextPage);
    }
  };

  const handleRefresh = () => {
    setCurrentPage(1);
    fetchJobs(1);
  };

  const handleApply = (job) => {
    if (onApply) {
      onApply(job);
    } else {
      Alert.alert('Apply Function', `Would apply to ${job.title} at ${job.company}`);
    }
  };

  // Filter companies by search
  const filteredJobs = jobs.filter(company =>
    company.name.toLowerCase().includes(search.toLowerCase())
  );

  const renderCompanyItem = ({ item }) => {
    const hasNew = item.jobs.some(isJobPostedToday);
    return (
      <LinearGradient
        colors={hasNew ? ['#e3ffe6', '#e0f7fa'] : ['#f8fafc', '#f1f8ff']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.companyCard}
      >
        <View style={styles.companyHeaderRow}>
          <View style={styles.logoContainer}>
            {COMPANY_LOGOS[item.name] ? (
              <Image
                source={{ uri: COMPANY_LOGOS[item.name] }}
                style={styles.companyLogo}
                resizeMode="contain"
              />
            ) : (
              <View style={styles.logoPlaceholder}>
                <Text style={styles.logoPlaceholderText}>
                  {item.name.charAt(0)}
                </Text>
              </View>
            )}
          </View>
          <View style={styles.companyHeaderText}>
            <Text style={styles.companyName}>{item.name}</Text>
            {hasNew && (
              <View style={styles.newBadge}>
                <Ionicons name="flame" size={16} color="#fff" />
                <Text style={styles.newBadgeText}>NEW</Text>
              </View>
            )}
          </View>
        </View>
        {item.jobs.length > 0 ? (
          <View>
            <View style={styles.jobIndicator}>
              <Ionicons name="briefcase" size={18} color="#2e7d32" style={{ marginRight: 4 }} />
              <Text style={styles.jobCount}>{item.jobs.length} SWE Intern Position{item.jobs.length > 1 ? 's' : ''}</Text>
            </View>
            <View style={styles.jobList}>
              {item.jobs.map(job => (
                <TouchableOpacity
                  key={job.id}
                  style={[styles.jobItem, isJobPostedToday(job) && styles.jobItemNew]}
                  onPress={() => handleApply(job)}
                  activeOpacity={0.85}
                >
                  <View style={styles.jobTitleRow}>
                    <Text style={styles.jobTitle}>{job.title}</Text>
                    {isJobPostedToday(job) && (
                      <View style={styles.jobNewBadge}>
                        <Text style={styles.jobNewBadgeText}>NEW</Text>
                      </View>
                    )}
                  </View>
                  <Text style={styles.jobLocation}>{job.location}</Text>
                  <Text style={styles.jobDate}>
                    <Ionicons name="calendar" size={14} color="#999" />{' '}
                    Posted: {isJobPostedToday(job) ? 'Today (NEW)' : new Date(job.posted_at).toLocaleDateString()}
                  </Text>
                  <TouchableOpacity
                    style={styles.viewDetailsButton}
                    onPress={() => Linking.openURL(job.url)}
                  >
                    <Ionicons name="open-outline" size={16} color="#fff" />
                    <Text style={styles.viewDetailsText}>View Details</Text>
                  </TouchableOpacity>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : (
          <View style={styles.noJobsContainer}>
            <Ionicons name="sad-outline" size={24} color="#e65100" style={{ marginBottom: 4 }} />
            <Text style={styles.noJobsText}>No SWE Intern positions for 2026</Text>
            <Text style={styles.checkLaterText}>Check back later</Text>
          </View>
        )}
      </LinearGradient>
    );
  };

  const renderEmptyState = () => {
    if (loading) return null;

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyTitle}>Loading Positions</Text>
        <Text style={styles.emptyText}>
          Checking all companies for Software Engineer Intern positions for 2026
        </Text>
        <ActivityIndicator size="large" color="#1e88e5" />
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={["#e3ffe6", "#e0f7fa", "#f8fafc"]}
        style={styles.headerGradient}
      >
        <Text style={styles.header}>SWE Internships 2026</Text>
        <Text style={styles.subHeader}>
          {totalCompanies} top companies monitored daily
        </Text>
        <View style={styles.searchBarContainer}>
          <Ionicons name="search" size={20} color="#888" style={{ marginLeft: 8 }} />
          <TextInput
            style={styles.searchBar}
            placeholder="Search companies..."
            value={search}
            onChangeText={setSearch}
            placeholderTextColor="#aaa"
          />
        </View>
      </LinearGradient>
      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={20} color="#721c24" style={{ marginBottom: 4 }} />
          <Text style={styles.errorText}>{error}</Text>
          <Button
            title="Try Again"
            onPress={fetchJobs}
            color="#1e88e5"
          />
        </View>
      )}
      <FlatList
        data={filteredJobs}
        renderItem={renderCompanyItem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.list}
        ListEmptyComponent={renderEmptyState()}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={["#1e88e5"]}
            tintColor="#1e88e5"
          />
        }
        onEndReached={loadMoreCompanies}
        onEndReachedThreshold={0.5}
        showsVerticalScrollIndicator={false}
      />
      <TouchableOpacity
        style={styles.fab}
        onPress={fetchJobs}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={["#1e88e5", "#43cea2"]}
          style={styles.fabGradient}
        >
          <Ionicons name="refresh" size={28} color="#fff" />
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerGradient: {
    paddingTop: 40,
    paddingBottom: 24,
    paddingHorizontal: 16,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
    marginBottom: 8,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
  },
  header: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 4,
    color: '#1a237e',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  subHeader: {
    fontSize: 16,
    color: '#5c6bc0',
    marginBottom: 16,
    textAlign: 'center',
  },
  searchBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 24,
    marginHorizontal: 8,
    marginTop: 8,
    marginBottom: 4,
    paddingHorizontal: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  searchBar: {
    flex: 1,
    height: 40,
    fontSize: 16,
    color: '#222',
    backgroundColor: 'transparent',
    marginLeft: 8,
  },
  list: {
    paddingBottom: 80,
    paddingHorizontal: 8,
  },
  companyCard: {
    borderRadius: 20,
    marginBottom: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.10,
    shadowRadius: 12,
    elevation: 6,
    backgroundColor: 'transparent',
  },
  companyHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  logoContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  companyLogo: {
    width: 64,
    height: 64,
    borderRadius: 12,
    backgroundColor: '#fff',
  },
  logoPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#bbdefb',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoPlaceholderText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0d47a1',
  },
  companyHeaderText: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  companyName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a237e',
    flex: 1,
    flexWrap: 'wrap',
  },
  newBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ff5252',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginLeft: 8,
  },
  newBadgeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 13,
    marginLeft: 4,
  },
  jobIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e8f5e9',
    padding: 8,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 12,
    marginTop: 2,
  },
  jobCount: {
    color: '#2e7d32',
    fontWeight: '600',
    fontSize: 15,
  },
  jobList: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  jobItem: {
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#f5f5f5',
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 10,
    paddingHorizontal: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 2,
  },
  jobItemNew: {
    borderColor: '#43cea2',
    borderWidth: 2,
    backgroundColor: '#e3ffe6',
  },
  jobTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  jobTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
    flexWrap: 'wrap',
  },
  jobNewBadge: {
    backgroundColor: '#43cea2',
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 1,
    marginLeft: 8,
  },
  jobNewBadgeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  jobLocation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  jobDate: {
    fontSize: 13,
    color: '#999',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  viewDetailsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e88e5',
    paddingVertical: 7,
    paddingHorizontal: 14,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 2,
  },
  viewDetailsText: {
    color: 'white',
    fontWeight: '500',
    marginLeft: 6,
    fontSize: 15,
  },
  noJobsContainer: {
    padding: 16,
    backgroundColor: '#fff3e0',
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  noJobsText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#e65100',
    marginBottom: 4,
  },
  checkLaterText: {
    fontSize: 14,
    color: '#f57c00',
    fontStyle: 'italic',
  },
  loader: {
    padding: 30,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
    color: '#555',
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
    color: '#777',
    marginBottom: 20,
    lineHeight: 24,
  },
  errorContainer: {
    padding: 20,
    backgroundColor: '#f8d7da',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#f5c6cb',
    marginBottom: 20,
    alignItems: 'center',
  },
  errorText: {
    color: '#721c24',
    fontSize: 16,
    marginBottom: 15,
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    zIndex: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.18,
    shadowRadius: 8,
    elevation: 8,
  },
  fabGradient: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default FavoriteCompanies;