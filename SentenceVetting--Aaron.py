# -*- coding: utf-8 -*-
#Aaron Shaw June 12, 2017--OpenStax, OpenFacts project

#imports
#import other project parts
from collections import defaultdict
import nltk
import TreetoList as listGen
import bookparse as parser
import random


"""
Finds all the useful sentences in a dictionary where the keys are the full sentences and values are parsed info
about the sentences.

Input--DF: list of sentences and values = parsed info about that sentence
	   key: glossary term

Output--result: list of relevant sentences
"""
def findDefSentences(df, key):
	sentences = df
	tagged_sentences = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in sentences)

	#checks if the key has multiple words
	if len(key.split(' ')) > 1:
		result = set()
		#iterates through each word of the key to find sentences related to it
		for w in key.split(' '):
			tagged = iterTaggedSentences(w, tagged_sentences, sentences)

	else:
		tagged = iterTaggedSentences(key, tagged_sentences, sentences)
	return tagged
	
"""
Iterates through all tagged sentences and determines if it is considered relevant or not.
Finds the idx of w and compares to the idx of the first verb. A sentence is relevant if w
index is before verb index

Input-- w: the key term, tagged_sentences: a list of parsed and tagged sentences, sentences:
		the original list of sentences that tagged_sentences came from

Output-- result: a sublist of sentences that were deemed relevant, backup: a testing list
		used in debugging that can be ignored
"""
def iterTaggedSentences(w, tagged_sentences, sentences):
	result = []
	backup = []
	if len(tagged_sentences) < 7:
		return (sentences, backup)

	#Find relevant sentences
	for s in tagged_sentences:
		#Finds index of verb and key
		vIdx = findVIndex(s)
		nIdx = findNIndex(s, w)
		sIdx = tagged_sentences.index(s)

		'''
		if nIdx != -1 and vIdx != -1 or len(s) < 6:
			result.append(sentences[sIdx])
		elif nIdx != -1 or len(sentences) < 6:
		elif nIdx != -1 or len(s) < 6:
			backup.append(sentences[sIdx])
		print(len(s), len(tagged_sentences), len(sentences))
		'''

		if nIdx != -1: 
			result.append(sentences[sIdx])
	
	return (result, backup)
			
"""
Gives a parsed sentence, finds the index of the first verb that appears in the sentence.

Input--sentence: a list of (word, tag) tuples

Output--index: the index of the verb if present (-1 if not present)
"""
def findVIndex(sentence):
	
	#find the first VB word in the sentence
	for word in sentence:
		tag = word[1]
		if tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ":

			return sentence.index(word)

	return -1
	
"""
Gives a parsed sentence, finds the index of the first key that appears in the sentence.

Input--sentence: a list of (word, tag) tuples
	   key: the term we are trying to find in the sentence

Output--index: the index of the verb if present (-1 if not present)
"""
def findNIndex(sentence,  key):
	
	#find the first key word in the sentence
	for word in sentence:
		tag = word[0].lower()
		if tag == key:
			return sentence.index(word)
	return -1    
	
	
"""
Runs the entire program. Generates lists of relevant sentences for a given
term and outouts those sentences and term to a .txt file. 

Can easily adjust which set of terms to examine. Simply adjust the range
of the "for term in terms" for loop.
"""	
def runTest():
	book = 'biology_raw.xhtml'
	#genereates a list of all glossary terms
	terms = parser.find_book_terms(book)
	#takes the xhtml tree and simplifies it into a more readible tree
	tree = parser.parse_into_tree(book)
	
	useful = 0
	notuseful = 0

	termDict = defaultdict(list)
	for term in terms[-10:-1]:

		listGen.makeFile(book, term, terms, tree)
		fileList = listGen.genSentences('output_file.txt')   
		sentences = listGen.listToString(fileList)
		importantSentences = findDefSentences(sentences, term)

		useful += len(importantSentences[0]) #extra info, can remove
		notuseful += len(fileList) #extra info, can remove
		termDict[term] += importantSentences[0]
		print(len(importantSentences[0]), len(sentences)) #extra info, can remove
		
		#WARNING CHANGED IMPORTANTSENTENCES TO A TUPLE, ORIGINIALLY A LIST
		if terms.index(term) % 100 == 0:
			print ("Completed " + str(terms.index(term)) + " of " + str(len(terms)) + " terms")
	
	
	f = open("useful_output.txt", 'w')
	for KV in termDict.keys():
		f.write(KV) 
		f.write("\n")
		value = termDict[KV]
		for v in value:
			f.write(v)
			f.write(" ")
		f.write("\n\n")
	print(useful, notuseful) #extra info, can remove


"""
Finds all relevant sentences to a given list of terms. Can be used
if you want to pick and choose what terms to search
"""
def genForTermsList(terms):

	termDict = defaultdict(list)
	book = 'biology_raw.xhtml'
	tree = parser.parse_into_tree(book)

	for term in terms:
		listGen.makeFile(book, term, terms, tree)
		fileList = listGen.genSentences('output_file.txt')   
		sentences = listGen.listToString(fileList)
		importantSentences = findDefSentences(sentences, term)

		termDict[term] += importantSentences[0]
	print(termDict)
		
		#WARNING CHANGED IMPORTANTSENTENCES TO A TUPLE, ORIGINIALLY A LIST
	
	f = open("useful_output.txt", 'w')
	for KV in termDict.keys():
		f.write(KV) 
		f.write("\n")
		value = termDict[KV]
		for v in value:
			f.write(v)
			f.write(" ")
		f.write("\n\n")



#runTest()

termsList = ['anaerobic', 
			'renal capsule',
			 'diabetes insipidus', 
			 'Apoda', 
			 'transitional epithelia',
			 'follicle stimulating hormone (FSH)',
			 'septa',
			 'loam', 
			 'lipid', 
			 'capillary', 
			 'progesterone', 
			 'testes', 
			 'hypothyroidism', 
			 'beta cell', 
			 'compliance']

#genForTermsList(termsList)



def secondRoundVetting(inDict) :
	oDict = defaultdict(list)
	f = open("useful_output.txt", 'w')
	scrubbed = defaultdict(list)
	for key in inDict.keys():
		val = inDict[key].split(". ")
		scrubbed[key] += val
	for key in scrubbed.keys():
		result = findDefSentences(scrubbed[key], key)
		#print(result)

		f.write(key) 
		f.write("\n")
		for sent in result:
			for v in sent:
				f.write(v)
				f.write(" ")
		f.write("\n\n")
		print(len(result))
		oDict[key] = result[0]
	print(oDict)




JacobVetting = { "lipid" :
				 "A glycolipid is also shown with the lipid portion embedded in the membrane and the carbohydrate portion jutting out of the membrane.  A phospholipid is a molecule consisting of glycerol, two fatty acids, and a phosphate-linked head group. The image on the left shows a spherical lipid bilayer.  The image on the right shows a smaller sphere that has a single lipid layer only.  This “elbow room” helps to maintain fluidity in the membrane at temperatures at which membranes with saturated fatty acid tails in their phospholipids would “freeze” or solidify. Why is emulsification important for digestion of lipids?  Bile aids in the digestion of lipids, primarily triglycerides by emulsification.  Lipids include fats, oils, waxes, phospholipids, and steroids. Phospholipids are responsible for the dynamic nature of the plasma membrane.  The hydrophobic tails of the phospholipids face one another while the hydrophilic head groups face outward. ",
				"testes" :
				"Hormonal control of the male reproductive system is mediated by the hypothalamus, anterior pituitary and testes.  LH causes the Leydig cells in the testes to secrete testosterone. Illustration shows a cross section of the penis and testes.  The testes, located immediately behind the penis, are covered by the scrotum.  Infertility can occur in land mammals when the testes do not descend through the abdominal cavity during fetal development. Sperm mature in seminiferous tubules that are coiled inside the testes, as illustrated in [link]. Sperm mature in seminiferous tubules in the testes.  The testes produce androgens, testosterone being the most prominent, which allow for the development of secondary sex characteristics and the production of sperm cells.  LH stimulates production of the sex hormones (androgens) by the interstitial cells of the testes and therefore is also called interstitial cell-stimulating hormone. The prostate gland is located in the testes. ",
				"follicle stimulating hormone (FSH)" : "",
				"diabetes insipidus" :
				"Chronic underproduction of ADH or a mutation in the ADH receptor results in diabetes insipidus.  Underproduction of ADH can cause diabetes insipidus. ",
				"loam" :
				"sandsiltclayloamAA soil consists of layers called ________ that taken together are called a ________. 002 mm in diameterhorizonsoil layer with distinct physical and chemical properties, which differs from other layers depending on how and when it was formedhumusorganic material of soil; made up of microorganisms, dead animals and plants in varying stages of decayloamsoil that has no dominant particle sizemineral soiltype of soil that is formed from the weathering of rocks and inorganic material; composed primarily of sand, silt, and clayO horizonlayer of soil with humus at the surface and decomposed vegetation at the baseorganic soiltype of soil that is formed from sedimentation; composed primarily of organic materialparent materialorganic and inorganic material in which soils formrhizospherearea of soil affected by root secretions and microorganismssandsoil particles between 0.  Some soils have no dominant particle size and contain a mixture of sand, silt, and humus; these soils are called loams.  The cricket (a) Gryllus pennsylvanicus prefers sandy soil, and the cricket (b) Gryllus firmus prefers loamy soil.  Soil inorganic material consists of rock slowly broken down into smaller particles that vary in size, such as sand, silt, and loam. ",
				"compliance" :
				"Compliance with the contraceptive method is a strong contributor to the success or failure rate of any particular method. Explain the importance of compliance and resistance in the lungs Lung Resistance and Compliance  The overall compliance of the lungs is increased, because as the alveolar walls are damaged, lung elastic recoil decreases due to a loss of elastic fibers, and more air is trapped in the lungs at the end of exhalation.  There is a decrease in compliance because the lung tissue cannot bend and move.  Two main causes of decreased gas exchange are compliance (how elastic the lung is) and resistance (how much obstruction exists in the airways).  If the compliance of the lung decreases, as occurs in restrictive diseases like fibrosis, the airways stiffen and collapse upon exhalation. Breathing and gas exchange are both altered by changes in the compliance and resistance of the lung. increase the compliance of the lungdecrease the compliance of the lungincrease the lung volumedecrease the work of breathingBAlveolar ventilation remains constant when ________. ",
				"septa" :
				 "Part A is an illustration of septated hyphae.  Like the septated hyphae, the coenocytic hyphae consist of long, branched fibers.  A bright field light micrograph of (c) Phialophora richardsiae shows septa that divide the hyphae.  Cells within the septated hyphae are rectangular.  In most phyla of fungi, tiny holes in the septa allow for the rapid flow of nutrients and small molecules from cell to cell along the hypha.  The hyphae in bread molds (which belong to the Phylum Zygomycota) are not separated by septa.  Conidia and asci, which are used respectively for asexual and sexual reproductions, are usually separated from the vegetative hyphae by blocked (non-perforated) septa.  Zygomycota (conjugated fungi) produce non-septated hyphae with many nuclei. 5 by 1 in) in size and divided into wedge-shaped lobules by connective tissue called septa.  Ribbon-like septa divide this cavity into segments.  Like the septa in anthozoans, the branched gastrovascular cells serve two functions: to increase the surface area for nutrient absorption and diffusion; thus, more cells are in direct contact with the nutrients in the gastrovascular cavity. ",
				"progesterone" :
				 "LH also plays a role in the development of ova, induction of ovulation, and stimulation of estradiol and progesterone production by the ovaries. Progesterone levels rise during the luteal phase of the ovarian cycle and the secretory phase of the uterine cycle.  The inhibition of FSH and LH prevents any further eggs and follicles from developing, while the progesterone is elevated. Estradiol and progesterone secreted from the corpus luteum cause the endometrium to thicken.  The levels of ovarian hormones estradiol and progesterone remain low.  Progesterone maintains the endometrium to help ensure pregnancy. LH and FSH are produced in the pituitary, and estradiol and progesterone are produced in the ovaries. Both progesterone and estradiol are produced by the follicles.  The placenta has taken over the functions of nutrition and waste and the production of estrogen and progesterone from the corpus luteum, which has degenerated. oxytocinestrogenβ-HCGprogesteroneAMajor organs begin to develop during which part of human gestation?  The two ovaries, which are located on either side of the uterus, secrete estradiol, progesterone, and inhibin. ",
				"beta cell" :
				"p53 can trigger apoptosis if certain cell cycle events fail.  HIV infects TH cells via their CD4 surface molecules, gradually depleting the number of TH cells in the body; this inhibits the adaptive immune system’s capacity to generate sufficient responses to infection or tumors.  These organelles were first observed by light microscopists in the late 1800s, where they appeared to be somewhat worm-shaped structures that seemed to be moving around in the cell. The amino acid-derived hormones epinephrine and norepinephrine bind to beta-adrenergic receptors on the plasma membrane of cells.  The liver releases IGFs, which cause target cells to take up amino acids, promoting protein synthesis. The vegetative body of a fungus is a unicellular or multicellular thallus. In the primary response to infection, antibodies are secreted first from plasma cells.  Other cellular factors recognize each signal sequence and help transport the protein from the cytoplasm to its correct compartment.  In humans, the different surface antigens are grouped into 24 different blood groups with more than 100 different antigens on each red blood cell. Blood clotting provides an example of the role of the extracellular matrix in cell communication. ",
				"hypothyroidism" :
				 "Hypothyroidism is a condition in which the thyroid gland is underactive. [link] Patient A has symptoms associated with decreased metabolism, and may be suffering from hypothyroidism.  Hypothyroidism is a condition in which the thyroid gland is underactive.  In children, hypothyroidism can cause cretinism, which can lead to mental retardation and growth defects.  Hypothyroidism, underproduction of the thyroid hormones, can cause a low metabolic rate leading to weight gain, sensitivity to cold, and reduced mental activity, among other symptoms.",
				"transitional epithelia" :
				 "Pinacocytes, which are epithelial-like cells, form the outermost layer of sponges and enclose a jelly-like substance called mesohyl.  They are most commonly found in a single layer representing a simple epithelia in glandular tissues throughout the body where they prepare and secrete glandular material. Transitional Epithelia Simple columnar epithelial cells absorb material from the digestive tract. Simple cuboidal epithelial cells are involved in the filtering of blood in the kidney.  [link] summarizes the different types of epithelial tissues. Pinacocytes are epithelial-like cells, form the outermost layer of sponges, and enclose a jelly-like substance called mesohyl. Which type of epithelial cell is best adapted to aid diffusion?  As a stratified epithelia, the surface cells can be sloughed off and the cells in deeper layers protect the underlying tissues from damage. The intestine is lined with epithelial cells with hair-like cilia extending into the intestinal lumen.  Inside the epithelial cells the fatty acids and monoglyerides are reassembled into triglycerides. ",
				"Apoda" : "",
				"renal capsule" :
				"The renal pelvis drains into the ureter.  There are two types of nephrons—cortical nephrons (85 percent), which are deep in the renal cortex, and juxtamedullary nephrons (15 percent), which lie in the renal cortex close to the renal medulla.  On the inside of the kidney, the renal pelvis branches out into two or three extensions called the major calyces, which further branch into the minor calyces.  The second part is called the loop of Henle, or nephritic loop, because it forms a loop (with descending and ascending limbs) that goes through the renal medulla.  Additionally, the loop of Henle invades the renal medulla, which is naturally high in salt concentration and tends to absorb water from the renal tubule and concentrate the filtrate.  In the loop of Henle, the filtrate exchanges solutes and water with the renal medulla and the vasa recta (the peritubular capillary network). The location of the adrenal glands on top of the kidneys is shown. This photograph shows the long slender stems, called setae, connected to capsules of the moss Thamnobryum alopecurum.  The second layer is called the perirenal fat capsule, which helps anchor the kidneys in place. The renal corpuscle, located in the renal cortex, is made up of a network of capillaries known as the glomerulus and the capsule, a cup-shaped chamber that surrounds it, called the glomerular or Bowman's capsule. The Bowman’s capsule surrounds the glomerulus. ",
				"capillary" :
				 "The histamines cause the capillary to become permeable.  Within the glomerulus, the network of capillaries is called the glomerular capillary bed.  In juxtamedullary nephrons, the peritubular capillary network forms a network around the loop of Henle and is called the vasa recta.  First, the nephrons filter blood that runs through the capillary network in the glomerulus.  A portal system carries blood from one capillary network to another; therefore, the hypophyseal portal system allows hormones produced by the hypothalamus to be carried directly to the anterior pituitary without first entering the circulatory system. Blood flow through the capillary beds is regulated depending on the body’s needs and is directed by nerve and hormone signals.  At any given moment only about 5-10% of our capillary beds actually have blood flowing through them. Illustration A shows an artery branching off into an arteriole, which branches into a capillary bed.  As blood moves into the arteries, arterioles, and ultimately to the capillary beds, the rate of movement slows dramatically to about 0.  This type of adhesion is called capillary action, and is illustrated in [link]. Capillary action in a glass tube is caused by the adhesive forces exerted by the internal surface of the glass exceeding the cohesive forces between the water molecules themselves.",
				"anaerobic" :
				 "In addition, some eukaryotes perform catabolic processes without oxygen (fermentation); that is, they perform or use anaerobic metabolism.  Early life forms, in blue, used anaerobic metabolism to obtain energy from their surroundings.  This means that they grow best in the presence of oxygen using aerobic respiration, but can survive using anaerobic respiration when oxygen is not available.  Methane (CH4) is produced when bacteria break down organic matter under anaerobic conditions. Some living eukaryotes are anaerobic and cannot survive in the presence of too much oxygen.  Such functions are often associated with the reduced mitochondrion-derived organelles of anaerobic eukaryotes. Anaerobic Cellular Respiration  Both methods are called anaerobic cellular respiration in which organisms convert energy for their use in the absence of oxygen.  Similarly, sulfate-reducing bacteria and Archaea, most of which are anaerobic ( [link]), reduce sulfate to hydrogen sulfide to regenerate NAD+ from NADH. Certain prokaryotes, including some species of bacteria and Archaea, use anaerobic respiration. "}

secondRoundVetting(JacobVetting)				
				
