# TODO: Import elephants, return object with each sequence containing elephants & locations
# TODO: Admin page
#
import json, time, urllib, re, sys, numbers,csv,datetime
from django.shortcuts import render, redirect
from .form import SequencesFileUploadForm, LocationsFileUploadForm, ElephantsFileUploadForm
from .models import Sequences, Locations, LocHapPub, Publications, LHPIndividual
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from datetime import datetime
from Bio import pairwise2, SeqIO


def admin(request):
  if not request.user.is_authenticated:
    return redirect("/login/")
  locGroups = []
  for location in Locations.objects.filter(oldPk=None):
    elephantsAtThisLocation = None
    hasElephants = False
    elephantsAtThisLocation = LocHapPub.objects.filter(location=location).filter(oldPk=None)
    if (len(elephantsAtThisLocation)) > 0:
      hasElephants = True

      elephantsAtThisLocation2 = []
      for e in elephantsAtThisLocation:
        accessionsList = [] #a list just because it's easier to join 
        for lhp in LHPIndividual.objects.filter(LHP=e.pk):
          accessionsList.append("%s (%s)"%(lhp.genBankAccession,lhp.numElephants))
        elephantsAtThisLocation2.append({"pk": e.pk, "haplotype": e.haplotype, "author":e.author, "datetimeModified":e.datetimeModified, "accessions":"<br/>".join(accessionsList)})
      locGroups.append({"location":location,"elephantsAtThisLocation":elephantsAtThisLocation2,"hasElephants":hasElephants});
  return render(request, "mapping/admin.html", {"epoch": time.time(),"locGroups":locGroups})


def urlPrefixes(request):
  domain = request.get_host()
  if domain == "localhost:8000":
    staticPrefix = ""
    urlPrefix = "/"
  elif domain == "192.168.0.123:8000":
    staticPrefix = ""
    urlPrefix = "/"
  elif domain == "76.211.73.91:61521":
    staticPrefix = ""
    urlPrefix = "/"
  elif domain == "192.168.1.67:8000":
    staticPrefix = ""
    urlPrefix = "/"
  elif domain == "testing.loxodontalocalizer.org:61080":
    staticPrefix = ""
    urlPrefix = "/"
  elif domain == "www.loxodontalocalizer.org":
    staticPrefix = "https://s3-us-west-2.amazonaws.com/zappa-bm4f8egmj"
    urlPrefix = "/"
  else:
    staticPrefix = "https://s3-us-west-2.amazonaws.com/zappa-bm4f8egmj"
    urlPrefix = "/dev/"
  return staticPrefix, urlPrefix


# STEP 0
def index(request):
  staticPrefix, urlPrefix = urlPrefixes(request)
  fastaTextInitial = ""
  if request.method == "POST":
    querySeq = request.POST["querySeq"]
    seqName = request.POST["seqName"]
    fastaTextInitial = ">%s\n%s" % (seqName, querySeq)
  haplotypeIds = LocHapPub.objects.all().values_list('haplotype_id',
                                                     flat=True)  # TODO: We need to make sure all haplotypes are in the elephants table
  seqDict = {}
  for seq in Sequences.objects.filter(id__in=haplotypeIds):
    seqDict[seq.id] = seq.seq
  context = {"fastaTextInitial": fastaTextInitial, "urlPrefix": urlPrefix, "staticPrefix": staticPrefix,
             "all_seqs": json.dumps(seqDict)}

  return render(request, "index.html", context)


def fromGoogleSpreadsheets(request):
  staticPrefix, urlPrefix = urlPrefixes(request)
  context = {"urlPrefix": urlPrefix, "staticPrefix": staticPrefix}
  return render(request, "mapping/fromGoogleSpreadsheets.html", context)

def createHaplotype(request):
  return render(request,"mapping/createHaplotype.html")


def createHaplotypeJson(request):
  if not (request.user.is_authenticated and request.method == "POST"):
    return redirect("/login/")

  try:
    
    seq = re.sub(r'\s+', '',request.POST["seq"]).upper()
    existingSeq = Sequences.objects.filter(seq=seq)
    if existingSeq.count() >0:
      return JsonResponse({"error": "Haplotype exists as %s"%existingSeq[0].pk}); #just get first one

    seqList = Sequences.objects.all();
    pkAsNum = []
    for seqObj in seqList:
      pkAsNum.append(int(seqObj.pk[2:]))
    nextPk = "LL%s"%(max(pkAsNum)+1)
    newSeq = Sequences.objects.create(pk=nextPk,seq=seq, datetimeModified=datetime.now(),
                                      lastEditedBy=request.user.username);
    return JsonResponse({"status": "success","pk":nextPk});
  except:
    print("Unexpected error:", sys.exc_info()[0])
  return JsonResponse({"status": "error", "error": str(sys.exc_info()[0])})



def createLocation(request):
  return createEditLocation(request,None)

def editLocation(request,locationID):
  return createEditLocation(request,locationID);

def migrateData(request):
  pass #disabled for safety
"""
  for lhpi in LHPIndividual.objects.all():
    gbaSL = lhpi.genBankAccession.split(",")
    if len(gbaSL)>1:
      for i in gbaSL:
        newEle = LHPIndividual.objects.create(LHP=lhpi.LHP, genBankAccession=i,
                                     numElephants=1, datetimeModified=datetime.now(),
                                     lastEditedBy="MigrationBot")
      print lhpi.pk
      lhpi.delete()


  for lhp in LocHapPub.objects.all():
    print lhp.id
    newEle = LHPIndividual.objects.create(LHP=lhp,genBankAccession = lhp.genebankAccession.strip(),
                                         numElephants = 1, datetimeModified = datetime.now(),
                                          lastEditedBy = "MigrationBot")
"""



def createEditLocation(request,locationID=None):
  elephantsAtThisLocation = None
  hasElephants = False
  if (locationID != None):
    location = Locations.objects.get(pk=locationID)  # TODO: What if not found?
    elephantsAtThisLocation = LocHapPub.objects.filter(location=location)
    if(len(elephantsAtThisLocation)) > 0:
      hasElephants = True
  else:
    location = None;  # create mode

  locations = Locations.objects.all();


  locDict = {};
  for loc in Locations.objects.filter(oldPk=None):
    locDict[loc.id] = {"locationName": loc.locationName, "lon": loc.lon, "lat": loc.lat,
                       "locationType": loc.locationType, "matchNotes": loc.matchNotes,
                       "locality": loc.locality, "accuracy": loc.accuracy}

  return render(request, "mapping/editLocation.html",
                {"hasElephants":hasElephants,"elephantsAtThisLocation":elephantsAtThisLocation,"location":location,"locDict": json.dumps(locDict),"locations": locations})


def editLocationJson(request):
  if not (request.user.is_authenticated and request.method == "POST"):
    return redirect("/login/")

  if(request.POST["locationID"]!=None and request.POST["locationID"]!=""):
    #make a "new" location that is a 'disabled' clone of the existing one. Then modify the
    #existing record. Thus, the PK isn't changed for the old, edited record

    try:
      loc = Locations.objects.get(pk=request.POST["locationID"]);
      newLoc = Locations.objects.create(locationName=loc.locationName,lon=loc.lon,
                                        lat=loc.lat,locationType=loc.locationType,
                                        matchNotes=loc.matchNotes,locality=loc.locality,
                                        accuracy=loc.accuracy,
                                        oldPk=loc.pk,datetimeModified=loc.datetimeModified,
                                        lastEditedBy=request.user.username);
      loc.locationName = request.POST["newName"];
      loc.lon = float(request.POST["newLon"]);
      loc.lat = float(request.POST["newLat"]);
      loc.locationType = request.POST["newType"];
      loc.matchNotes = request.POST["newMatchNotes"];
      loc.locality = request.POST["newLocality"];
      loc.accuracy = int(request.POST["newAccuracy"]);
      loc.datetimeModified = datetime.now();
      loc.lastEditNotes = request.POST["newLastEditNotes"];
      loc.save()
      return JsonResponse({"status": "success"});
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return JsonResponse({"status": "error", "error": str(sys.exc_info()[0])})

  else:
    print "create mode"
    try:
      newLoc = Locations.objects.create(locationName=request.POST["newName"],
                                        lon=float(request.POST["newLon"]),
                                        lat=float(request.POST["newLat"]),
                                        locationType=request.POST["newType"],
                                        matchNotes=request.POST["newMatchNotes"],
                                        locality=request.POST["newLocality"],
                                        accuracy=int(request.POST["newAccuracy"]),
                                        datetimeModified=datetime.now(),
                                        lastEditNotes=request.POST["newLastEditNotes"],
                                        lastEditedBy=request.user.username);

      return JsonResponse({"status": "success"});
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return JsonResponse({"status": "error", "error": str(sys.exc_info()[0])})




def createElephant(request):
  return createEditElephant(request, None)

def editElephant(request, elephantID):
  return createEditElephant(request, elephantID)


def createEditElephant(request, elephantID=None):
  if request.user.is_authenticated:
    genBankAccessions = []
    lhpiList = []
    if (elephantID != None):
      elephant = LocHapPub.objects.get(pk=elephantID)  # TODO: What if not found?
      for lhpi in LHPIndividual.objects.filter(LHP=elephant):
        gba = lhpi.genBankAccession
        if gba == None:
          gba = ""
        numEle = lhpi.numElephants
        if numEle == None:
          numEle = ""
        lhpiList.append({"genBankAccession":gba,"numElephants":numEle})
    else:
      elephant = None;  # create mode

    sequences = Sequences.objects.filter(oldPk=None);
    locations = Locations.objects.filter(oldPk=None);
    seqDict = {};
    locDict = {};
    pubDict = {};
    for seq in Sequences.objects.filter(oldPk=None):
      seqDict[seq.id] = seq.seq;

    for pub in Publications.objects.filter(oldPk=None):
      pubDict[pub.id] = {"author": pub.author, "paperurl": pub.paperurl}
    for loc in Locations.objects.filter(oldPk=None):
      locDict[loc.id] = {"locationName": loc.locationName, "lon": loc.lon, "lat": loc.lat,
                         "locationType": loc.locationType, "matchNotes": loc.matchNotes,
                         "locality": loc.locality, "accuracy": loc.accuracy}

    return render(request, "mapping/editElephant2.html",
                  {"lhpiList":json.dumps(lhpiList),"pubDict": json.dumps(pubDict), "seqDict": json.dumps(seqDict), "locDict": json.dumps(locDict),
                   "elephant": elephant, "sequences": sequences, "locations": locations,"genBankAccessions":"\n".join(genBankAccessions)})
  else:
    return redirect("/login")


def editElephantJson(request):
  if not (request.user.is_authenticated and request.method == "POST"):
    print "Not authenticated"  # TODO make json response

  if(request.POST["elephantID"]!=None and request.POST["elephantID"]!=""):

    #make a "new" elephant that is a 'disabled' clone of the existing one. Then modify the
    #existing record. Thus, the PK isn't changed for the old, edited record
    try:
      ele = LocHapPub.objects.get(pk=request.POST["elephantID"]);
      newEle = LocHapPub.objects.create(location=ele.location, haplotype=ele.haplotype,
                                        author=ele.author, oldPk=ele.pk, datetimeModified=ele.datetimeModified,
                                        lastEditedBy=request.user.username);
      ele.author = Publications.objects.get(pk=(request.POST["newAuthor"]));
      ele.location= Locations.objects.get(pk=request.POST["newLocation"]);
      ele.haplotype = Sequences.objects.get(pk=request.POST["newHaplotype"]);
      
      #delete all LHPindividuals linking to this and then re-add them
      for lhpi in LHPIndividual.objects.filter(LHP=ele):
        lhpi.delete()
      lhpiList = json.loads(request.POST["lhpiList"])

      noInserts = True #monitor if we didn't insert anything
      for lhpi in lhpiList:
        if(lhpi["genBankAccession"].strip()==""):
          gba = None
        else:
          gba = lhpi["genBankAccession"].strip()
       
        try:
          numEle =  int(lhpi["numElephants"].strip())
          if (numEle < 1):
            numEle = 0
        except:
          numEle = None
        if numEle == None and gba == None:
          continue #don't insert if both are blank
        newLHPI = LHPIndividual.objects.create(LHP=ele, genBankAccession=gba,
                                                numElephants=numEle, datetimeModified=datetime.now(),lastEditedBy=request.user.username, lastEditNotes=request.POST["newLastEditNotes"])
        noInserts = False
      if noInserts: #if no inserts for LHPI, just default to 1
        newLHPI = LHPIndividual.objects.create(LHP=ele, genBankAccession=None,
                                                numElephants=None, datetimeModified=datetime.now(),lastEditedBy=request.user.username, lastEditNotes=request.POST["newLastEditNotes"])
      ele.datetimeModified = datetime.now();
      ele.lastEditNotes = request.POST["newLastEditNotes"];
      print 'last edit notes%s'%request.POST["newLastEditNotes"]
      ele.save()
      return JsonResponse({"status": "success"})
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return JsonResponse({"status":"error", "error":str(sys.exc_info()[0])})
  else:
    print "create mode"
    try:
      newEle = LocHapPub.objects.create(location=Locations.objects.get(pk=request.POST["newLocation"]),
                                        haplotype=Sequences.objects.get(pk=request.POST["newHaplotype"]),

                                        author=Publications.objects.get(pk=(request.POST["newAuthor"])),
                                        datetimeModified=datetime.now(),
                                        lastEditNotes=request.POST["newLastEditNotes"],
                                        lastEditedBy=request.user.username);
      lhpiList = json.loads(request.POST["lhpiList"])
      noInserts = True #monitor if we didn't insert anything
      for lhpi in lhpiList:
        if(lhpi["genBankAccession"].strip()==""):
          gba = None
        else:
          gba = lhpi["genBankAccession"].strip()
       
        try:
          numEle =  int(lhpi["numElephants"].strip())
          if (numEle < 1):
            numEle = 0
        except:
          numEle = None
        if numEle == None and gba == None:
          continue #don't insert if both are blank
        newLHPI = LHPIndividual.objects.create(LHP=newEle, genBankAccession=gba,
                                                numElephants=numEle, datetimeModified=datetime.now(),lastEditedBy=request.user.username, lastEditNotes=request.POST["newLastEditNotes"])
        noInserts = False
      if noInserts: #if no inserts for LHPI, just default to 1
        newLHPI = LHPIndividual.objects.create(LHP=newEle, genBankAccession=None,
                                                numElephants=None, datetimeModified=datetime.now(),lastEditedBy=request.user.username, lastEditNotes=request.POST["newLastEditNotes"])
      return JsonResponse({"status": "success"})
    except:
      print("Unexpected error:", sys.exc_info()[0])
      return JsonResponse({"status": "error", "error": str(sys.exc_info()[0])})


def editElephantSubmit(request):  # TODO this function is not used, can delete
  if request.user.is_authenticated and request.method == "POST":
    # first, check if anything changed.
    ele = LocHapPub.objects.get(pk=request.POST["elephant_id"]);

    changed = []
    newAuthorID = int(request.POST["select-author"]);
    if ele.author.pk != newAuthorID:
      changed.append("author");
    newGenebankAccession = request.POST["genebankAccession"];
    if ele.genebankAccession != newGenebankAccession:
      changed.append("genebankAccession");

    newLocationID = int(request.POST["select-location"]);
    if (ele.location.pk != newLocationID):
      changed.append("location");

    newSequenceID = request.POST["select-haplotype"];
    if (ele.haplotype.pk != newSequenceID):
      changed.append("haplotype");

    if len(changed) == 0:
      print "error, nothing changed";
      return;  # TODO return html template
    else:
      newEle = LocHapPub.objects.create(location=ele.location, haplotype=ele.haplotype,
                                        genebankAccession=ele.genebankAccession,
                                        author=ele.author, oldPk=ele.pk, datetimeModified=ele.datetimeModified);
      ele.author.pk = newAuthorID;
      ele.location.pk = newLocationID;
      ele.haplotype.pk = newSequenceID;
      ele.genebankAccession = newGenebankAccession;
      ele.datetimeModified = datetime.now();
      ele.save()

      print "made new elephant";  # TODO return to main edit page, with success message
  else:
    print "editElephantSubmitError";  # TODO return to main edit page with error message

def getCsv(request):
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="allDB.csv"'
  writer = csv.writer(response)
  writer.writerow("lhpi.pk,lhpi.genBankAccession,lhpi.numElephants,lhpi.datetimeModified,lhpi.lastEditedBy,lhpi.lastEditNotes,lhp.pk,lhp.lastEditedBy,lhp.lastEditNotes,loc.locationName,loc.lon,loc.lat,loc.locationType,loc.matchNotes,loc.locality,loc.accuracy,loc.datetimeModified,loc.lastEditedBy,loc.lastEditNotes,pub.author,pub.paperurl,pub.datetimeModified,pub.lastEditedBy,pub.lastEditNotes,hap.seq,hap.datetimeModified,hap.lastEditedBy,hap.lastEditNotes".split(","))
  for lhpi in LHPIndividual.objects.all():
    try:
      returnArr = [lhpi.pk,lhpi.genBankAccession,lhpi.numElephants,lhpi.datetimeModified,lhpi.lastEditedBy,lhpi.lastEditNotes]
      lhp = LocHapPub.objects.get(pk=lhpi.LHP_id) #should actually only have one item
      returnArr.extend([lhp.pk,lhp.lastEditedBy,lhp.lastEditNotes])
      loc = Locations.objects.get(pk=lhp.location.pk) #should actually only have one item
      returnArr.extend([loc.locationName,loc.lon,loc.lat,loc.locationType,loc.matchNotes,loc.locality,loc.accuracy,loc.datetimeModified,loc.lastEditedBy,loc.lastEditNotes])
      pub = Publications.objects.get(pk=lhp.author.pk) #should actually only have one item
      returnArr.extend([pub.author,pub.paperurl,pub.datetimeModified,pub.lastEditedBy,pub.lastEditNotes])
      hap = Sequences.objects.get(pk=lhp.haplotype.pk)
      returnArr.extend([hap.pk,hap.seq,hap.datetimeModified,hap.lastEditedBy,hap.lastEditNotes])

      returnArrUnicode = []
      for s in returnArr:
        if isinstance(s, numbers.Number) or isinstance(s, datetime):
          returnArrUnicode.append(str(s).encode("utf-8"))
        elif s == None:
          returnArrUnicode.append("".encode("utf-8"))
        else:
          returnArrUnicode.append(s.encode("utf-8"))
      writer.writerow(returnArrUnicode)
    except:
      pass
  return response
    

# Step 1
def aligning(request):
  staticPrefix, urlPrefix = urlPrefixes(request)
  highestScore = 0 # if we don't have a highest score of 309 or higher, we give an error
  if request.method != "POST":
    return redirect("/")
  #implied else

  inputSeq = request.POST["fastaText"]
  seqs = {}
  if inputSeq.strip()[0] == ">":
    seqName = None
    seq = None
    for line in inputSeq.splitlines():
      if line[0] == ">":
        if seqName != None:  # if we already have a sequence
          seqs[seqName] = re.sub(r'\s+', '', seq)
        seqName = line[1:]
        seq = ""
      else:
        seq += line
    seqs[seqName] = re.sub(r'\s+', '', seq).upper()  # get last one
  else:  # assume not FASTA format
    seqs["input"] = re.sub(r'\s+', '', inputSeq).upper()
  keys = list(seqs.keys())
  firstSeqKey = keys[0]
  firstSeq = seqs[keys[0]]

  # check for length
  # check for characters
  errors = []
  nonLegitChars = re.sub(r'[ACGT]', '', firstSeq)
  if len(nonLegitChars) > 0:
    errors.append("Your FASTA sequence has characters other than 'ACGT'. Ambiguous bases are not supported")
  if len(firstSeq) != 316:
    errors.append(
      "Your sequence is contains %s bp. The mitochondrial control region input should contain 316 bp." % len(
        firstSeq))
  if len(errors) > 0:
    return render(request, "mapping/errors.html",
                  {"urlPrefix": urlPrefix, "staticPrefix": staticPrefix, "inputSeq": firstSeq,
                    "errors": errors})
  #implied else
  alignments = []
  querySeq = firstSeq
  seqName = firstSeqKey
  aligned = 0
  subjects = Sequences.objects.filter(oldPk=None);
  for i in range(len(subjects)):
    subject = subjects[i]
    subjectSeq = re.sub(r'\s+', '',subjects[i].seq).upper()
    alignmentObj = pairwise2.align.globalms(querySeq, subjectSeq, 1, 0, -1, -1, one_alignment_only=True)[0]
    elephants = LocHapPub.objects.filter(haplotype=subject).filter(oldPk=None)
    elephantObjs = []
    if len(elephants) == 0:
      continue  # TODO: Handle the situation when a haplotype has no elephants
    for e in elephants:
      tempAccessionList = []
      indivs = []  #to be used in the future for map drawing

      try:
        for indiv in LHPIndividual.objects.filter(LHP=e):
    
          if indiv.genBankAccession != "":
            indivs.append({"accession":indiv.genBankAccession,"numElephants":indiv.numElephants})
            tempAccessionList.append( "<a href='https://www.ncbi.nlm.nih.gov/nucleotide/%s' target='_blank'>%s</a>"%(indiv.genBankAccession,indiv.genBankAccession))
     
        eo = {"id": e.pk, "author": e.author.author, "paperurl": e.author.paperurl,
              "locationID":e.location.pk, "genbankAccessionHTML": ", ".join(tempAccessionList),
              "indivs": indivs, "locationName": e.location.locationName,
              "lon": e.location.lon, "lat": e.location.lat, "locationType": e.location.locationType,
              "matchNotes": e.location.matchNotes, "locality": e.location.locality,
              "accuracy": e.location.accuracy}
        elephantObjs.append(eo)
      except Exception as e2:
        print e.pk
        print e2
    highestScore = max(highestScore, int(alignmentObj[2]))
    alignments.append({"elephants": elephantObjs, "subjectID": subject.id, "alignmentQ": alignmentObj[0],
                        "alignmentS": alignmentObj[1], "score": int(alignmentObj[2]),
                        "mismatch": 316 - alignmentObj[2], "match": alignmentObj[4]})
  if highestScore < 309:
    return render(request, "mapping/errors.html",
              {"urlPrefix": urlPrefix, "staticPrefix": staticPrefix, "inputSeq": firstSeq,
                "errors": ["There was an error with your input sequence, which showed up as more than 7 mismatches to the nearest African elephant sequence. Your input may not be from an African elephant or not be homologous to the required 316 bp mitochondrial control region sequence. Please contact us if you have questions."]})
  return generateAlignmentOutput(request,alignments,seqName,querySeq)

def generateAlignmentOutput(request,alignments,seqName,querySeq):
  letterDict = {} # dictionary used to assign letters to the elephant pins
  locationPinsDict = {} #shows the best result for each location

  staticPrefix, urlPrefix = urlPrefixes(request)
  alignmentsSorted = sorted(alignments, key=lambda k: k['score'], reverse=True)
  hadFinalScoreLine = False
  lastScore = None
  elephantNum = 0
  for alignment in alignmentsSorted:
    s = alignment["alignmentS"]
    q = alignment["alignmentQ"]
    if lastScore == None:
      scoreLine = False
      finalScoreDisclaimer = False  # do nothing for first line
    elif alignment['score'] > 313 and lastScore != alignment['score']:
      scoreLine = True
      finalScoreDisclaimer = False
    elif not hadFinalScoreLine and alignment['score'] <= 313:
      scoreLine = True
      hadFinalScoreLine = True
      finalScoreDisclaimer = True
    else:
      scoreLine = False
      finalScoreDisclaimer = False
    lastScore = alignment['score']
    if len(q) != len(s):
      print "uh-oh, alignment lengths differ"  # TODO: More formally define error
    alignment["alignmentToPrint"], alignment["mismatch"] = formatLineToPrint(q, s)
    alignment["scoreLine"] = scoreLine
    alignment["finalScoreDisclaimer"] = finalScoreDisclaimer

    for e in alignment["elephants"]:

      if (alignment["mismatch"] < 1 and elephantNum < 26):
        currLetter = getLetter(letterDict,e["locationID"],alignment['score'])
        makeLocationsPin(locationPinsDict,staticPrefix,e,alignment["subjectID"],alignment["score"],alignment['mismatch'],currLetter)
        e["smallimage"] = "//maps.google.com/mapfiles/kml/paddle/%s-ugc-lv.png" % currLetter
        e["image"] = "//maps.google.com/mapfiles/kml/paddle/%s-ugc.png" % currLetter
      elif e["accuracy"] > 0:
        makeLocationsPin(locationPinsDict,staticPrefix,e,alignment["subjectID"],alignment["score"],alignment['mismatch'])
        e["smallimage"] = staticPrefix + "/static/images/accuracy1.png"
        e["image"] = "//maps.google.com/mapfiles/kml/paddle/red-circle.png"
      else:
        makeLocationsPin(locationPinsDict,staticPrefix,e,alignment["subjectID"],alignment["score"],alignment['mismatch'])
        e["smallimage"] = staticPrefix + "/static/images/accuracy0.png"
        e["image"] = "//maps.google.com/mapfiles/kml/paddle/red-blank.png"
      elephantNum += 1

  return render(request, "mapping/results.html",
                {"seqName":seqName,"datetime":datetime.utcnow(),"isAuthenticated": request.user.is_authenticated, "epoch": time.time(), "seqName": seqName,
                  "querySeq": querySeq, "urlPrefix": urlPrefix, "staticPrefix": staticPrefix,
                  "alignments": alignmentsSorted, "alignmentsJSON": json.dumps(alignmentsSorted),"locationPinsDict":json.dumps(locationPinsDict)})


def makeLocationsPin(locationPinsDict,staticPrefix,lhp,subjectID,score,mismatch,letter=None):
  #assume lhp's come in sorted order, so will only append if it's the best scoring one
  locationID = lhp["locationID"]
  if locationID not in locationPinsDict:
    if letter!=None:
      smallimage = "//maps.google.com/mapfiles/kml/paddle/%s-ugc-lv.png" % letter
      image = "//maps.google.com/mapfiles/kml/paddle/%s-ugc.png" % letter
    elif lhp["accuracy"] > 0:
      smallimage = staticPrefix + "/static/images/accuracy1.png"
      image = "//maps.google.com/mapfiles/kml/paddle/red-circle.png"
    else:
      smallimage = staticPrefix + "/static/images/accuracy0.png"
      image = "//maps.google.com/mapfiles/kml/paddle/red-circle.png"
    locationPinsDict[locationID] = {"score":score,"mismatch":mismatch,"locationName":lhp["locationName"],"locality":lhp["locality"],
      "locationType":lhp["locationType"],"locality":lhp["locality"],"accuracy":lhp["accuracy"],"letter":letter,"authors":[],"subjectID":subjectID,"lhp_ids":[],
      "smallimage":smallimage,"image":image,"lat":lhp["lat"],"lon":lhp["lon"]}
  if locationPinsDict[locationID]["score"] == score: #only if it's also the highest score   
    locationPinsDict[locationID]["authors"].append(lhp["author"])
    locationPinsDict[locationID]["lhp_ids"].append(lhp["id"])
    locationPinsDict[locationID]["authors"] = list(set(locationPinsDict[locationID]["authors"]))  #make unique

#unique letter for every locationID + score pair
def getLetter(letterDict,locationID,score):
  LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  key = str(locationID) + "_" + str(score)

  if key in letterDict:
    print LETTERS[letterDict[key]]
    return LETTERS[letterDict[key]]
  #implicit else
  letterDict[key] = len(letterDict.keys()) #gets the next index and puts it as the value
  return LETTERS[letterDict[key]]


def formatLineToPrint(q, s):
  alignmentToPrint = "";
  bottom = ""
  mismatches = 0
  for i in range(len(s)):
    if q[i] == s[i]:
      bottom += "."
    else:
      bottom += s[i]
      mismatches += 1
  i = 0;
  while (i < len(s)):
    if i == 0:
      increment = 31  # make a line break every 40 chars
      alignmentToPrint += "Query:&nbsp;&nbsp;&nbsp;%s<br/>Subject:&nbsp;%s<br/>" % (
        q[i:(i + increment)], bottom[i:(i + increment)])
    else:
      increment = 40
      alignmentToPrint += "%s<br/>%s<br/>" % (q[i:(i + increment)], bottom[i:(i + increment)])
    i += increment
  return alignmentToPrint.replace(" ", "&nbsp"), mismatches
