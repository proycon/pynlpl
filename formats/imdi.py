RELAXNG_IMDI = """
<!--
	XML Schema for IMDI
	
	Version 3.0.13
	
	Max-Planck Institute for Psycholinguistics
-->
<!--
	
3.0.15, 2009-11-17, Alexander Koenig
	in session
	Changed maxOccurs for the Content fields SubGenre, Task, Modalities and Subject from unbounded to 1

3.0.14, 2009-08-17, Dieter Van Uytvanck
	Addition of an optional CatalogueHandle attribute to Corpus

3.0.13, 2009-08-06, Evelyn Richter
	In catalogue
	Allowed projects to occur multiple times because one corpus could be collected from different projects (decision with Paul Trilsbeek)
	
3.0.12, 2009-07-13, Evelyn Richter
	In catalogue
	Deleted BeginYear and EndYear elements, data to be put into Date element in format YYYY/YYYY (decision with Daan Broeder)
	Changed Authors element to "Author" in the singular (not compatible with 3-4 existing catalogue files, users have to be informed, decision with Daan Broeder)
	Allowed multiple Publisher elements (decision with Dieter van Uytvanck)
	Allowed multiple author elements (decision with Daan Broeder)
	Added Image as subelement of Format (decision with Paul Trilsbeek)
	Added Text and Image as subelements of Quality (decision with Daan Broeder)

3.0.11, 2009-06-18, Peter Withers
	In session
	Added Link, DefaultLink and Type attributes to Boolean_Type

3.0.10, 2009-06-15, Evelyn Richter
	In catalogue
	Allowed multiple content types and multiple locations and 
	added elements "ContactPerson", "BeginYear", "EndYear", 
	"ReferenceLink", "MetadataLink", "Publications" in Catalogue 
	schema to accommodate for CLARIN resources 
	(multiple resource types and countries possible for CLARIN resources,
	frequent occurrence of information for which elements were created)
	Allowed multiple publisher elements in catalogue after discussion with Dieter van Uytvanck

3.0.9, 2009-04-17
	made ISO-3 language codes possible

3.0.8, 2008-08-05, Daan Broeder
	In lexicon resource  en lexicon component
	removed schema reference 
	made description in Lexiconresource optional
	made description in MetaLanguages optional
	made language in MetaLanguages optional

3.0.7, 2008-03-04, Jacquelijn Ringersma
	In lexicon resource bundle 
	MediaResourceLink vervangen door ReferenceResourceLink
	en Multiple schemareferences mogelijk gemaakt 	

-->
<rng:grammar xmlns:rng="http://relaxng.org/ns/structure/1.0" xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:imdi="http://www.mpi.nl/IMDI/Schema/IMDI" ns="http://www.mpi.nl/IMDI/Schema/IMDI" datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
	<!-- 
		Main schema
	-->
	<rng:start combine="choice">
<rng:ref name="METATRANSCRIPT"/>
</rng:start>
<rng:define name="METATRANSCRIPT">
<rng:element name="METATRANSCRIPT">
<rng:ref name="METATRANSCRIPT_Type"/>
		<a:documentation>
			The root element for IMDI descriptions
		</a:documentation>
	</rng:element>
</rng:define>
	<!-- 
		Schema for vocabulary definition
	-->
	<rng:start combine="choice">
<rng:ref name="VocabularyDef"/>
</rng:start>
<rng:define name="VocabularyDef">
<rng:element name="VocabularyDef">
<rng:ref name="VocabularyDef_Type"/>
		<a:documentation>
			Instantiation of a VocabularyDef_Type
		</a:documentation>
	</rng:element>
</rng:define>
	<!-- 
		METATRANSCRIPT
	-->
	<rng:define name="METATRANSCRIPT_Type">
		
			<rng:optional>
<rng:element name="History">
<rng:ref name="String_Type"/>
				<a:documentation>
					Revision history of the metadata description
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:choice>
				<rng:oneOrMore>
<rng:element name="Session">
<rng:ref name="Session_Type"/>
</rng:element>
</rng:oneOrMore>
				<rng:oneOrMore>
<rng:element name="Corpus">
<rng:ref name="Corpus_Type"/>
</rng:element>
</rng:oneOrMore>
				<rng:element name="Catalogue">
<rng:ref name="Catalogue_Type"/>
</rng:element>
			</rng:choice>
		
		<rng:optional>
<rng:attribute name="Profile">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:attribute name="Date">
<rng:data type="date"/>
</rng:attribute>
		<rng:optional>
<rng:attribute name="Originator">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:attribute name="Version">
<rng:data type="string"/>
</rng:attribute>
		<rng:attribute name="FormatId">
<rng:data type="string"/>
</rng:attribute>
		<rng:optional>
<rng:attribute name="History">
<rng:data type="anyURI"/>
</rng:attribute>
</rng:optional>
		<rng:attribute name="Type">
<rng:ref name="Metatranscript_Value_Type"/>
</rng:attribute>
		<rng:optional>
<rng:attribute name="ArchiveHandle">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Location
	-->
	<rng:define name="Location_Type">
		<a:documentation>
			Information on creation location for this data
		</a:documentation>
		
			<rng:element name="Continent">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The name of a continent
				</a:documentation>
			</rng:element>
			<rng:element name="Country">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The name of a country
				</a:documentation>
			</rng:element>
			<rng:zeroOrMore>
<rng:element name="Region">
<rng:ref name="String_Type"/>
				<a:documentation>
					The name of a geographic region
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
			<rng:optional>
<rng:element name="Address">
<rng:ref name="String_Type"/>
				<a:documentation>
					The address
				</a:documentation>
			</rng:element>
</rng:optional>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!--
		Key
	-->
	<rng:define name="Key_Type">
		
			
				<rng:attribute name="Name">
<rng:data type="string"/>
</rng:attribute>
			
		
	</rng:define>
	<!-- 
		Keys
	-->
	<rng:define name="Keys_Type">
		<a:documentation>
			List of a number of key name value pairs. Should be used to add information that is not covered by other metadata elements at this level
		</a:documentation>
		
			<rng:zeroOrMore>
<rng:element name="Key">
<rng:ref name="Key_Type"/>
</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Languages
	-->
	<rng:define name="Languages_Type">
		<a:documentation>
			Groups information about the languages used in the session
		</a:documentation>
		
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for the list of languages spoken by this participant
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
			<rng:zeroOrMore>
<rng:element name="Language">
<rng:ref name="Language_Type"/>
</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!--
		Access
	-->
	<rng:define name="Access_Type">
		<a:documentation>
			Groups information about access rights for this data
		</a:documentation>
		
			<rng:element name="Availability">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Availability of the data
				</a:documentation>
			</rng:element>
			<rng:element name="Date">
<rng:ref name="Date_Type"/>
				<a:documentation>
					Date when access rights were evaluated
				</a:documentation>
			</rng:element>
			<rng:element name="Owner">
<rng:ref name="String_Type"/>
				<a:documentation>
					Name of owner resource
				</a:documentation>
			</rng:element>
			<rng:element name="Publisher">
<rng:ref name="String_Type"/>
				<a:documentation>
					Publisher responsible for distribution of this data
				</a:documentation>
			</rng:element>
			<rng:element name="Contact">
<rng:ref name="Contact_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		External Resource Reference
	-->
	<rng:define name="ExternalResourceReference_Type">
		<a:documentation>
			Resource is preferably a metadata resource. In the case of a well-defined merged metadata/content format such as TEI or legacy resources for which no further metadata is available it is the resource itself. If the external resource is an IMDI session with written resources Type &amp; SubType will be the same as the Type &amp; SubType of the primary written resource in that session. If it is a session with IMDI multi-media resources the Type of the Media
				File will designate it. SubType is used only for written resources. Non-IMDI metadata resource types need to be mapped to IMDI types
		</a:documentation>
		
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The type of the external (metadata) resource
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="SubType">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The sub type of the external (metadata) resource. Only used in case its metadata for a written resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The metadata format
				</a:documentation>
			</rng:element>
			<rng:element name="Link">
<rng:data type="anyURI">
				<a:documentation>
					The URL of the external metadata record
				</a:documentation>
			</rng:data>
</rng:element>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Project
	-->
	<rng:define name="Project_Type">
		<a:documentation>
			Project Information
		</a:documentation>
		
			<rng:element name="Name">
<rng:ref name="String_Type"/>
				<a:documentation>
					A short name or abbreviation for the project
				</a:documentation>
			</rng:element>
			<rng:element name="Title">
<rng:ref name="String_Type"/>
				<a:documentation>
					The full title of the project
				</a:documentation>
			</rng:element>
			<rng:element name="Id">
<rng:ref name="String_Type"/>
				<a:documentation>
					A unique identifier for the project
				</a:documentation>
			</rng:element>
			<rng:element name="Contact">
<rng:ref name="Contact_Type"/>
				<a:documentation>
					Contact information for this project
				</a:documentation>
			</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for this project
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Metadata Group
	-->
	<rng:define name="MDGroupType">
		<a:documentation>
			Type for group of metadata pertaining to a session
		</a:documentation>
		
			<rng:element name="Location">
<rng:ref name="Location_Type"/>
				<a:documentation>
					Groups information about the location where the session was created
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Project">
<rng:ref name="Project_Type"/>
				<a:documentation>
					Groups information about the project for which the session was (originally) created
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
				<a:documentation>
					Project keys
				</a:documentation>
			</rng:element>
			<rng:element name="Content">
<rng:ref name="Content_Type"/>
				<a:documentation>
					Groups information about the content of the session. The content description takes place in several (overlapping) dimensions
				</a:documentation>
			</rng:element>
			<rng:element name="Actors">
<rng:ref name="Actors_Type"/>
				<a:documentation>
					Groups information about all actors in the session
				</a:documentation>
			</rng:element>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Content
	-->
	<rng:define name="Content_Type">
		
			<rng:element name="Genre">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Major genre classification
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="SubGenre">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Sub genre classification
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Task">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					List of he major tasks carried out in the session
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Modalities">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					List of modalities used in the session
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Subject">
				<a:documentation>
					Classifies the subject of the session. Uses preferably an existing library classification scheme such as LCSH. The element has a scheme attribute that indicates what scheme is used. Comments: The element can be repeated but the user should guarantee consistency
				</a:documentation>
				
					
						
							
							<rng:attribute name="Encoding">
<rng:data type="string"/>
</rng:attribute>
						
					
				
			</rng:element>
</rng:optional>
			<rng:element name="CommunicationContext">
				<a:documentation>
					This groups information concerning the context of communication
				</a:documentation>
				
					
						<rng:optional>
<rng:element name="Interactivity">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								degree of interactivity
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="PlanningType">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Degree of planning of the event
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Involvement">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Indicates in how far the researcher was involved in the linguistic event
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="SocialContext">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Indicates the social context the event took place in
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="EventStructure">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Indicates the structure of the communication event
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Channel">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Indicates the channel of the communication
							</a:documentation>
						</rng:element>
</rng:optional>
					
				
			</rng:element>
			<rng:element name="Languages">
<rng:ref name="Languages_Type"/>
</rng:element>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for the content of this session
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Actors
	-->
	<rng:define name="Actors_Type">
		
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description about the actors as a group
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
			<rng:zeroOrMore>
<rng:element name="Actor">
<rng:ref name="Actor_Type"/>
				<a:documentation>
					Group of actors
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Actor
	-->
	<rng:define name="Actor_Type">
		
			<rng:element name="Role">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Functional role of the actor e.g. consultant, contributor, interviewer, researcher, publisher, collector, translator
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Name">
<rng:ref name="String_Type"/>
				<a:documentation>
					Name of the actor as used by others in the transcription
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:element name="FullName">
<rng:ref name="String_Type"/>
				<a:documentation>
					Official name of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Code">
<rng:ref name="String_Type"/>
				<a:documentation>
					Short unique code to identify the actor as used in the transcription
				</a:documentation>
			</rng:element>
			<rng:element name="FamilySocialRole">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The family social role of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Languages">
<rng:ref name="Languages_Type"/>
				<a:documentation>
					The actor languages
				</a:documentation>
			</rng:element>
			<rng:element name="EthnicGroup">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The ethnic groups of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Age">
<rng:ref name="AgeRange_Type"/>
				<a:documentation>
					The age of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="BirthDate">
<rng:ref name="Date_Type"/>
				<a:documentation>
					The birthdate of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Sex">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The sex of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Education">
<rng:ref name="String_Type"/>
				<a:documentation>
					The education of the actor
				</a:documentation>
			</rng:element>
			<rng:element name="Anonymized">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Indicates if real names or anonymized codes are used to identify the actor
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="Contact">
<rng:ref name="Contact_Type"/>
				<a:documentation>
					Contact information of the actor
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
				<a:documentation>
					Actor keys
				</a:documentation>
			</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for this individual actor
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
		
		<rng:optional>
<rng:attribute name="ResourceRef">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Corpus
	-->
	<rng:define name="Corpus_Type">
		<a:documentation>
			Type for a corpus that points to either other corpora or sessions
		</a:documentation>
		
			<rng:element name="Name">
<rng:ref name="String_Type"/>
				<a:documentation>
					Name of the (sub-)corpus
				</a:documentation>
			</rng:element>
			<rng:element name="Title">
<rng:ref name="String_Type"/>
				<a:documentation>
					Title for the (sub-)corpus
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description of the (sub-)corpus
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:optional>
<rng:element name="MDGroup">
<rng:ref name="MDGroupType"/>
</rng:element>
</rng:optional>
			<rng:zeroOrMore>
<rng:element name="CorpusLink">
<rng:ref name="CorpusLink_Type"/>
</rng:element>
</rng:zeroOrMore>
		
		<rng:optional>
<rng:attribute name="SearchService">
<rng:data type="anyURI"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="CorpusStructureService">
<rng:data type="anyURI"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="CatalogueLink">
<rng:data type="anyURI"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="CatalogueHandle">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Corpus Link
	-->
	<rng:define name="CorpusLink_Type">
		<a:documentation>
			Link to other resource. Attribute name is for the benefit of browsing
		</a:documentation>
		
			
				<rng:attribute name="Name">
<rng:data type="string"/>
</rng:attribute>
			
		
	</rng:define>
	<!--
		Catalogue
	-->
	<rng:define name="Catalogue_Type">
		<a:documentation>
			Type for group metadata pertaining to published corpora
		</a:documentation>
		
			<rng:element name="Name">
<rng:ref name="String_Type"/>
				<a:documentation>
					Name of the published corpus
				</a:documentation>
			</rng:element>
			<rng:element name="Title">
<rng:ref name="String_Type"/>
				<a:documentation>
					Title of the published corpus
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Id">
<rng:ref name="String_Type"/>
				<a:documentation>
					Identifier of the published corpus
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:oneOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description of the published corpus
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:element name="DocumentLanguages">
				<a:documentation>
					The languages used for documentation of the corpus
				</a:documentation>
				
					
						<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
							<a:documentation>
								Description for the list of languages
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="Language">
<rng:ref name="SimpleLanguageType"/>
</rng:element>
</rng:zeroOrMore>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:element name="SubjectLanguages">
				<a:documentation>
					The languages in the corpus that are subject of analysis
				</a:documentation>
				
					
						<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
							<a:documentation>
								Description for the list of languages
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="Language">
<rng:ref name="SubjectLanguageType"/>
</rng:element>
</rng:zeroOrMore>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Location">
<rng:ref name="Location_Type"/>
</rng:element>
</rng:oneOrMore>
			<rng:oneOrMore>
<rng:element name="ContentType">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Content type of the published corpus
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:element name="Format">
				
					<rng:interleave>
<rng:optional>
<rng:optional>
<rng:element name="Text">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Audio">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Video">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Image">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
</rng:interleave>
				
			</rng:element>
			<rng:element name="Quality">
				
					<rng:interleave>
<rng:optional>
<rng:optional>
<rng:element name="Text">
<rng:ref name="Quality_Value_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Audio">
<rng:ref name="Quality_Value_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Video">
<rng:ref name="Quality_Value_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
<rng:optional>
<rng:optional>
<rng:element name="Image">
<rng:ref name="Quality_Value_Type"/>
</rng:element>
</rng:optional>
</rng:optional>
</rng:interleave>
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:element name="SmallestAnnotationUnit">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
			<rng:element name="Applications">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
			<rng:element name="Date">
<rng:ref name="Date_Type"/>
</rng:element>
			<rng:oneOrMore>
<rng:element name="Project">
<rng:ref name="Project_Type"/>
</rng:element>
</rng:oneOrMore>
			<rng:oneOrMore>
<rng:element name="Publisher">
<rng:ref name="String_Type"/>
				<a:documentation>
					Publisher responsible for distribution of the published corpus
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:oneOrMore>
<rng:element name="Author">
<rng:ref name="CommaSeparatedString_Type"/>
				<a:documentation>
					Authors for the resources
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:element name="Size">
<rng:ref name="String_Type"/>
				<a:documentation>
					Human readabusle string that indicates total size of corpus
				</a:documentation>
			</rng:element>
			<rng:element name="DistributionForm">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:element name="Pricing">
<rng:ref name="String_Type"/>
				<a:documentation>
					Pricing info of the corpus
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="ContactPerson">
<rng:ref name="String_Type"/>
				<a:documentation>
					Person to be contacted about the resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="ReferenceLink">
<rng:ref name="String_Type"/>
				<a:documentation>
					URL to the resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="MetadataLink">
<rng:ref name="String_Type"/>
				<a:documentation>
					URL to the metadata for the resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Publications">
<rng:ref name="String_Type"/>
				<a:documentation>
					List of any publications related to the resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Session
	-->
	<rng:define name="Session_Type">
		
			<rng:element name="Name">
<rng:ref name="String_Type"/>
</rng:element>
			<rng:element name="Title">
<rng:ref name="String_Type"/>
</rng:element>
			<rng:element name="Date">
<rng:ref name="DateRange_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="ExternalResourceReference">
<rng:ref name="ExternalResourceReference_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:element name="MDGroup">
<rng:ref name="MDGroupType"/>
</rng:element>
			<rng:element name="Resources">
				<a:documentation>
					Groups information of language resources connected to the session
				</a:documentation>
				
					
						<rng:zeroOrMore>
<rng:element name="MediaFile">
<rng:ref name="MediaFile_Type"/>
							<a:documentation>
								Groups all media resources
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="WrittenResource">
<rng:ref name="WrittenResource_Type"/>
							<a:documentation>
								Groups information about a Written Resource
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="LexiconResource">
<rng:ref name="LexiconResource_Type"/>
							<a:documentation>
								Groups information only pertaining to a Lexical resource
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="LexiconComponent">
<rng:ref name="LexiconComponent_Type"/>
							<a:documentation>
								Groups information only pertaining to a lexiconComponent
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="Source">
<rng:ref name="Source_Type"/>
							<a:documentation>
								Groups information about the source; e.g. media-carrier, book, newspaper archive etc.
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
						<rng:optional>
<rng:element name="Anonyms">
<rng:ref name="Anonyms_Type"/>
							<a:documentation>
								Groups data about name conversions for persons who are anonymised
							</a:documentation>
						</rng:element>
</rng:optional>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:optional>
<rng:element name="References">
				<a:documentation>
					Groups information about external documentation associated with this session
				</a:documentation>
				
					
						<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
							<a:documentation>
								Every description is a reference
							</a:documentation>
						</rng:element>
</rng:zeroOrMore>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
</rng:optional>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		MediaFile
	-->
	<rng:define name="MediaFile_Type">
		<a:documentation>
			Groups information about the media file
		</a:documentation>
		
			<rng:element name="ResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to media file
				</a:documentation>
			</rng:element>
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Major part of mime-type
				</a:documentation>
			</rng:element>
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Minor part of mime-type
				</a:documentation>
			</rng:element>
			<rng:element name="Size">
<rng:ref name="String_Type"/>
				<a:documentation>
					Size of media file
				</a:documentation>
			</rng:element>
			<rng:element name="Quality">
<rng:ref name="Quality_Type"/>
				<a:documentation>
					Quality of the recording
				</a:documentation>
			</rng:element>
			<rng:element name="RecordingConditions">
<rng:ref name="String_Type"/>
				<a:documentation>
					describes technical conditions of recording
				</a:documentation>
			</rng:element>
			<rng:element name="TimePosition">
<rng:ref name="TimePositionRange_Type"/>
</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:optional>
<rng:attribute name="ResourceId">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Written Resource
	-->
	<rng:define name="WrittenResource_Type">
		<a:documentation>
			Groups information about a Written Resource
		</a:documentation>
		
			<rng:element name="ResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to file containing the annotations/transcription
				</a:documentation>
			</rng:element>
			<rng:element name="MediaResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to media file from which the annotations/transcriptions originate 
				</a:documentation>
			</rng:element>
			<rng:element name="Date">
				<a:documentation>
					Date when Written Resource was created
				</a:documentation>
				
					
						
					
				
			</rng:element>
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The type of the WrittenResource
				</a:documentation>
			</rng:element>
			<rng:element name="SubType">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The subtype of the WrittenResource
				</a:documentation>
			</rng:element>
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					File format used for Written Resource
				</a:documentation>
			</rng:element>
			<rng:element name="Size">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The size of the Written Resource file. Integer value with addition of M (mega) or K (kilo)
				</a:documentation>
			</rng:element>
			<rng:element name="Validation">
<rng:ref name="Validation_Type"/>
</rng:element>
			<rng:element name="Derivation">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					How this document relates to another resource
				</a:documentation>
			</rng:element>
			<rng:element name="CharacterEncoding">
<rng:ref name="String_Type"/>
				<a:documentation>
					Character encoding used in the written resource
				</a:documentation>
			</rng:element>
			<rng:element name="ContentEncoding">
<rng:ref name="String_Type"/>
				<a:documentation>
					Content encoding used in the written resource
				</a:documentation>
			</rng:element>
			<rng:element name="LanguageId">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Language used in the resource
				</a:documentation>
			</rng:element>
			<rng:element name="Anonymized">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Indicates if data has been anonymised. CV boolean
				</a:documentation>
			</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:optional>
<rng:attribute name="ResourceId">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Lexicon Resource
	-->
	<rng:define name="LexiconResource_Type">
		<a:documentation>
			Groups information only pertaining to a Lexical resource
		</a:documentation>
		
			<rng:element name="ResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to lexical resource
				</a:documentation>
			</rng:element>
			<rng:element name="Date">
<rng:ref name="Date_Type"/>
				<a:documentation>
					Date when lexical resource was created
				</a:documentation>
			</rng:element>
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The type of the WrittenResource
				</a:documentation>
			</rng:element>
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The format of the LexicalResource
				</a:documentation>
			</rng:element>
			<rng:element name="CharacterEncoding">
<rng:ref name="String_Type"/>
				<a:documentation>
					The character encoding of the LexicalResource
				</a:documentation>
			</rng:element>
			<rng:element name="Size">
				<a:documentation>
					The size of the LexicalResource in bytes
				</a:documentation>
				
					
						
							<rng:ref name="ProfileAttributes"/>
						
					
				
			</rng:element>
			<rng:element name="NoHeadEntries">
<rng:ref name="Integer_Type"/>
				<a:documentation>
					The number of head entries of the LexicalResource
				</a:documentation>
			</rng:element>
			<rng:element name="NoSubEntries">
<rng:ref name="Integer_Type"/>
				<a:documentation>
					The number of sub entries of the LexicalResource
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="LexicalEntry">
				
					
						<rng:element name="HeadWordType">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: Sentence, Phrase, Wordform, Lemma, ...
							</a:documentation>
						</rng:element>
						<rng:element name="Orthography">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: HyphenatedSpelling, SyllabifiedSpelling, ...
							</a:documentation>
						</rng:element>
						<rng:element name="Morphology">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: Stem,StemALlomorphy, Segmentation, ...
							</a:documentation>
						</rng:element>
						<rng:element name="MorphoSyntax">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: POS, Inflexion, Countability, ...
							</a:documentation>
						</rng:element>
						<rng:element name="Syntax">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: Complementation, Alternation, Modification, ...
							</a:documentation>
						</rng:element>
						<rng:element name="Phonology">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: Transcription, IPA Transcription, CV pattern, ...
							</a:documentation>
						</rng:element>
						<rng:element name="Semantics">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								OCV: Sense dstinction
							</a:documentation>
						</rng:element>
						<rng:element name="Etymology">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
						<rng:element name="Usage">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
						<rng:element name="Frequency">
<rng:ref name="String_Type"/>
</rng:element>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
</rng:oneOrMore>
			<rng:element name="MetaLanguages">
				<a:documentation>
					A block to describe the languages that are used to define terms, to describe meaning
				</a:documentation>
				
					
						<rng:zeroOrMore>
<rng:element name="Language">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
</rng:zeroOrMore>
						<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:optional>
<rng:attribute name="ResourceId">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- LMF compliant Lexicon component -->
	<rng:define name="LexiconComponent_Type">
		<a:documentation>
			Groups information only pertaining to a lexiconComponent
		</a:documentation>
		
			<rng:element name="ResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to lexiconComponent
				</a:documentation>
			</rng:element>
			<rng:element name="Date">
<rng:ref name="Date_Type"/>
				<a:documentation>
					Date when lexiconComponent was created
				</a:documentation>
			</rng:element>
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The type of the lexiconComponent
				</a:documentation>
			</rng:element>
			<!-- Type element is not very relevant for lexiconComponent, since the IMDI type will be 'unspecified' -->
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					The format of the lexiconComponent
				</a:documentation>
			</rng:element>
			<rng:element name="CharacterEncoding">
<rng:ref name="String_Type"/>
				<a:documentation>
					The character encoding of the lexiconComponent
				</a:documentation>
			</rng:element>
			<rng:element name="Size">
				<a:documentation>
					The size of the lexiconComponent in bytes
				</a:documentation>
				
					
						
							<rng:ref name="ProfileAttributes"/>
						
					
				
			</rng:element>
			<rng:element name="Component">
				<a:documentation>
					Describes the tree in which the component can be embedded
				</a:documentation>
				
					
						<rng:element name="possibleParents">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Describes the possible parents of the lexiconComponent in the schema tree
							</a:documentation>
						</rng:element>
						<rng:optional>
<rng:element name="preferredParent">
<rng:ref name="Vocabulary_Type"/>
							<a:documentation>
								Descibes the preferred parent of the lexiconComponent in the schema tree
							</a:documentation>
						</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="childNodes">
							
								
									<rng:optional>
<rng:element name="childComponents">
<rng:ref name="Vocabulary_Type"/>
										<a:documentation>
											Describes the possible component children of the lexiconComponent in the schema tree
										</a:documentation>
									</rng:element>
</rng:optional>
									<rng:optional>
<rng:element name="childCategories">
<rng:ref name="Vocabulary_Type"/>
										<a:documentation>
											Describes the possible category children of the lexiconComponent in the schema tree
										</a:documentation>
									</rng:element>
</rng:optional>
								
							
						</rng:element>
</rng:optional>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:optional>
<rng:element name="LexicalInfo">
				<a:documentation>
					Gives information on the lexical applications of the lexiconComponent
				</a:documentation>
				
					
						<rng:optional>
<rng:element name="Orthography">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add orthography to the lexicon schema
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Morphology">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add morphology to the lexicon schema.
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="MorphoSyntax">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add morphosyntactic features to the lexicon schema
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Syntax">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add syntactic features to the lexicon schema
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Phonology">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add phonology to the lexicon schema.
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Semantics">
<rng:data type="boolean">
							<a:documentation>
								Describes whether the lexiconComponent can be used to add a semantic element to the lexicon schema
							</a:documentation>
						</rng:data>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Etymology">
<rng:data type="boolean"/>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Usage">
<rng:data type="boolean"/>
</rng:element>
</rng:optional>
						<rng:optional>
<rng:element name="Frequency">
<rng:data type="boolean"/>
</rng:element>
</rng:optional>
					
				
			</rng:element>
</rng:optional>
			<rng:element name="MetaLanguages">
				<a:documentation>
					A block to describe the languages that are used to define terms, to describe meaning
				</a:documentation>
				
					
						<rng:element name="Language">
<rng:ref name="Vocabulary_Type"/>
</rng:element>
						<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
					
					<rng:ref name="ProfileAttributes"/>
				
			</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:optional>
<rng:attribute name="ResourceId">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!--
		Source
	-->
	<rng:define name="Source_Type">
		<a:documentation>
			Groups information about the original source; e.g. media-carrier, book, newspaper archive etc.
		</a:documentation>
		
			<rng:element name="Id">
				<a:documentation>
					Unique code to identify the original source
				</a:documentation>
				
					
						
							<rng:ref name="ProfileAttributes"/>
						
					
				
			</rng:element>
			<rng:element name="Format">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Physical storage format of the source
				</a:documentation>
			</rng:element>
			<rng:element name="Quality">
<rng:ref name="Quality_Type"/>
				<a:documentation>
					Quality of original recording
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="CounterPosition">
<rng:ref name="CounterPosition_Type"/>
</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="TimePosition">
<rng:ref name="TimePositionRange_Type"/>
</rng:element>
</rng:optional>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for the original source
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
			<rng:element name="Keys">
<rng:ref name="Keys_Type"/>
</rng:element>
		
		<rng:ref name="ProfileAttributes"/>
		<rng:optional>
<rng:attribute name="ResourceRefs">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
	</rng:define>
	<!-- 
		Anonyms
	-->
	<rng:define name="Anonyms_Type">
		<a:documentation>
			Groups data about name conversions for persons who are anonymised
		</a:documentation>
		
			<rng:element name="ResourceLink">
<rng:ref name="ResourceLink_Type"/>
				<a:documentation>
					URL to information to convert pseudo named to real-names
				</a:documentation>
			</rng:element>
			<rng:element name="Access">
<rng:ref name="Access_Type"/>
</rng:element>
		
	</rng:define>
	<!-- 
		Vocabulary Definition
	-->
	<rng:define name="VocabularyDef_Type">
		<a:documentation>
			The definition of a vocabulary. Attributes: Date of creattion, Link to origin. Contails a Description be element to descr+++ ibe the domain of the vocabulary and a (unspecified) number of value enries
		</a:documentation>
		
			<rng:oneOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:oneOrMore>
			<rng:oneOrMore>
<rng:element name="Entry">
				
					
						
							<rng:attribute name="Tag">
<rng:data type="string"/>
</rng:attribute>
							<rng:attribute name="Value">
<rng:data type="string"/>
</rng:attribute>
						
					
				
			</rng:element>
</rng:oneOrMore>
		
		<rng:attribute name="Name">
<rng:data type="string"/>
</rng:attribute>
		<rng:attribute name="Date">
<rng:data type="date"/>
</rng:attribute>
		<rng:optional>
<rng:attribute name="Tag">
<rng:data type="date"/>
</rng:attribute>
</rng:optional>
		<rng:attribute name="Link">
<rng:ref name="Link_Value_Type"/>
</rng:attribute>
	</rng:define>
	<!-- 
		Description
	-->
	<rng:define name="Description_Type">
		<a:documentation>
			Human readable description in the form of a text with language id specification and/or a link to a file with a description and language id specification. The name attribute is to name the link (if present)
		</a:documentation>
		
			
				<rng:attribute name="LanguageId">
<rng:ref name="LanguageId_Value_Type"/>
</rng:attribute>
				<rng:attribute name="Name">
<rng:data type="string"/>
</rng:attribute>
				<rng:attribute name="ArchiveHandle">
<rng:data type="string"/>
</rng:attribute>
				<rng:attribute name="Link">
<rng:data type="anyURI"/>
</rng:attribute>
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!--
		Contact
	-->
	<rng:define name="Contact_Type">
		<a:documentation>
			Contact information for this data
		</a:documentation>
		
			<rng:optional>
<rng:element name="Name">
<rng:ref name="String_Type"/>
</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Address">
<rng:ref name="String_Type"/>
</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Email">
<rng:ref name="String_Type"/>
</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Organisation">
<rng:ref name="String_Type"/>
</rng:element>
</rng:optional>
		
	</rng:define>
	<!-- 
		Validation
	-->
	<rng:define name="Validation_Type">
		<a:documentation>
			The validation used for the resource
		</a:documentation>
		
			<rng:element name="Type">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					CV: content, type, manual, automatic, semi-automatic
				</a:documentation>
			</rng:element>
			<rng:element name="Methodology">
<rng:ref name="Vocabulary_Type"/>
				<a:documentation>
					Validation methodology
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="Level">
<rng:ref name="Integer_Type"/>
				<a:documentation>
					Percentage of resource validated
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
</rng:element>
</rng:zeroOrMore>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Age
	-->
	<rng:define name="Age_Type">
		<a:documentation>
			Specifies age of a person with differerent counting methods
		</a:documentation>
		
			
				<rng:attribute xmlns:ns_1="http://relaxng.org/ns/compatibility/annotations/1.0" name="AgeCountingMethod" ns_1:defaultValue="SinceBirth">
<rng:ref name="AgeCountingMethod_Value_Type"/>
</rng:attribute>
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Age Range
	-->
	<rng:define name="AgeRange_Type">
		<a:documentation>
			Specifies age of a person in the form of a range
		</a:documentation>
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Language Type
		At the moment this type is used both as a sub element of Actor and of Project.
		Future versions of this schema should ensure that different Language Types are used, so that for example MotherTongue cannot be set when the Language refers to a Project.
	-->
	<rng:define name="Language_Type">
		<a:documentation>
			An element from a set of languages used in the session
		</a:documentation>
		
			<rng:element name="Id">
<rng:ref name="LanguageId_Type"/>
				<a:documentation>
					Unique code to identify a language
				</a:documentation>
			</rng:element>
			<rng:oneOrMore>
<rng:element name="Name">
<rng:ref name="LanguageName_Type"/>
				<a:documentation>
					Name of the language
				</a:documentation>
			</rng:element>
</rng:oneOrMore>
			<rng:optional>
<rng:element name="MotherTongue">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Is it the speakers mother tongue. Only applicable if used in the context of a speakers language
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="PrimaryLanguage">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Is it the speakers primary language. Only applicable if used in the context of a speakers language
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="Dominant">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Is it the most frequently used language in the document. Only applicable if used in the context of the resource's language
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="SourceLanguage">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Direction of translation. Only applicable in case it is the context of a lexicon resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:optional>
<rng:element name="TargetLanguage">
<rng:ref name="Boolean_Type"/>
				<a:documentation>
					Direction of translation. Only applicable in case it is the context of a lexicon resource
				</a:documentation>
			</rng:element>
</rng:optional>
			<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
				<a:documentation>
					Description for this particular language
				</a:documentation>
			</rng:element>
</rng:zeroOrMore>
		
		<rng:optional>
<rng:attribute name="ResourceRef">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Subject Language
	-->
	<rng:define name="SubjectLanguageType">
		
			<rng:ref name="SimpleLanguageType"/>
				
					<rng:optional>
<rng:element name="Dominant">
<rng:ref name="Boolean_Type"/>
						<a:documentation>
							Indicates if language is dominant language
						</a:documentation>
					</rng:element>
</rng:optional>
					<rng:optional>
<rng:element name="SourceLanguage">
<rng:ref name="Boolean_Type"/>
						<a:documentation>
							Indicates if language is source language
						</a:documentation>
					</rng:element>
</rng:optional>
					<rng:optional>
<rng:element name="TargetLanguage">
<rng:ref name="Boolean_Type"/>
						<a:documentation>
							Indicates if language is target language
						</a:documentation>
					</rng:element>
</rng:optional>
					<rng:zeroOrMore>
<rng:element name="Description">
<rng:ref name="Description_Type"/>
						<a:documentation>
							Description of the language
						</a:documentation>
					</rng:element>
</rng:zeroOrMore>
				
			
		
	</rng:define>
	<!-- 
		Simple Language
	-->
	<rng:define name="SimpleLanguageType">
		<a:documentation>
			Information on language name and id
		</a:documentation>
		
			<rng:element name="Id">
<rng:ref name="LanguageId_Type"/>
				<a:documentation>
					Unique code to identify a language
				</a:documentation>
			</rng:element>
			<rng:element name="Name">
<rng:ref name="LanguageName_Type"/>
				<a:documentation>
					The name of the language
				</a:documentation>
			</rng:element>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!--
		Language Id
	-->
	<rng:define name="LanguageId_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!--
		Language Name
	-->
	<rng:define name="LanguageName_Type">
		
			
		
	</rng:define>
	<!--
		Basic Types 
	-->
	<!-- 
		Boolean
	-->
	<rng:define name="Boolean_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
				<rng:attribute xmlns:ns_1="http://relaxng.org/ns/compatibility/annotations/1.0" name="Type" ns_1:defaultValue="ClosedVocabulary">
<rng:ref name="VocabularyType_Value_Type"/>
</rng:attribute>
				<rng:attribute name="DefaultLink">
<rng:ref name="Link_Value_Type"/>
</rng:attribute>
				<rng:attribute name="Link">
<rng:ref name="Link_Value_Type"/>
</rng:attribute>
			
		
	</rng:define>
	<!-- 
		String
	-->
	<rng:define name="String_Type">
		<a:documentation>
			String type for single spaced, single line strings
		</a:documentation>
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Comma Separated String
	-->
	<rng:define name="CommaSeparatedString_Type">
		<a:documentation>
			Comma separated string
		</a:documentation>
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Integer
	-->
	<rng:define name="Integer_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!--
		Date
	-->
	<rng:define name="Date_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Date Range
	-->
	<rng:define name="DateRange_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Age Value
	-->
	<rng:define name="Age_Value_Type">
		<a:documentation>
			The age of a person
		</a:documentation>
		<rng:data type="string">
			<rng:param name="pattern">([0-9]+)*(;[0-9]+)*(.[0-9]+)*|Unknown|Unspecified</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		Age Range Value
	-->
	<rng:define name="AgeRange_Value_Type">
		<a:documentation>
			The age of a person given as a range
		</a:documentation>
		<rng:data type="string">
			<rng:param name="pattern">([0-9]+)?(;[0-9]+)?(.[0-9]+)?(/([0-9]+)?(;[0-9]+)?(.[0-9]+)?)?|Unknown|Unspecified</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		Age Counting Method Value
	-->
	<rng:define name="AgeCountingMethod_Value_Type">
		<a:documentation>
			The age counting method
		</a:documentation>
		<rng:choice>
			<rng:value>SinceConception</rng:value>
			<rng:value>SinceBirth</rng:value>
		</rng:choice>
	</rng:define>
	<!--
		Resource Link
	-->
	<rng:define name="ResourceLink_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
				<rng:attribute name="ArchiveHandle">
<rng:data type="string"/>
</rng:attribute>
			
		
	</rng:define>
	<!-- 
		Vocabulary
	-->
	<rng:define name="Vocabulary_Type">
		<a:documentation>
			Vocabulary content and attributes
		</a:documentation>
		
			
				<rng:attribute xmlns:ns_1="http://relaxng.org/ns/compatibility/annotations/1.0" name="Type" ns_1:defaultValue="OpenVocabulary">
<rng:ref name="VocabularyType_Value_Type"/>
</rng:attribute>
				<rng:attribute name="DefaultLink">
<rng:ref name="Link_Value_Type"/>
</rng:attribute>
				<rng:attribute name="Link">
<rng:ref name="Link_Value_Type"/>
					<a:documentation>
						Link to a vocabulary definition
					</a:documentation>
				</rng:attribute>
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Counter Position
	-->
	<rng:define name="CounterPosition_Type">
		<a:documentation>
			Position (start (+end) ) on a old fashioned tape without time indication
		</a:documentation>
		
			<rng:element name="Start">
<rng:ref name="Integer_Type"/>
</rng:element>
			<rng:optional>
<rng:element name="End">
<rng:ref name="Integer_Type"/>
</rng:element>
</rng:optional>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Time Position
	-->
	<rng:define name="TimePosition_Type">
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!-- 
		Time Position Range
	-->
	<rng:define name="TimePositionRange_Type">
		<a:documentation>
			Position in a media file or modern tape
		</a:documentation>
		
			<rng:element name="Start">
<rng:ref name="TimePosition_Type"/>
				<a:documentation>
					The start time position of a recording
				</a:documentation>
			</rng:element>
			<rng:optional>
<rng:element name="End">
<rng:ref name="TimePosition_Type"/>
				<a:documentation>
					The end time position of a recording
				</a:documentation>
			</rng:element>
</rng:optional>
		
		<rng:ref name="ProfileAttributes"/>
	</rng:define>
	<!-- 
		Quality
	-->
	<rng:define name="Quality_Type">
		<a:documentation>
			Quality indication
		</a:documentation>
		
			
				<rng:ref name="ProfileAttributes"/>
			
		
	</rng:define>
	<!--
		Value Types
	-->
	<!-- 
		Empty Value
	-->
	<rng:define name="Empty_Value_Type">
		<a:documentation>
			Unspecified is a non-existing (null) value. Unknown is a informational value indicating that the real value is not known
		</a:documentation>
		<rng:choice>
			<rng:value>Unknown</rng:value>
			<rng:value>Unspecified</rng:value>
		</rng:choice>
	</rng:define>
	<!-- 
		Empty String Value
	-->
	<rng:define name="EmptyString_Value_Type">
		<a:documentation>
			empty string definition
		</a:documentation>
		<rng:data type="string">
			<rng:param name="maxLength">0</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		Comma Separated String Value
	-->
	<rng:define name="CommaSeparatedString_Value_Type">
		<a:documentation>
			Comma seperated string
		</a:documentation>
		<rng:data type="string">
			<rng:param name="pattern">[^,]*(,[^,]+)*</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		Boolean Value
	-->
	<rng:define name="Boolean_Value_Type">
		<a:documentation>
			Loose boolean value where empty values are allowed
		</a:documentation>
		<rng:choice>
<rng:data type="boolean">xsd:boolean imdi:Empty_Value_Type</rng:data>
<rng:ref name="Empty_Value_Type"/>xsd:boolean imdi:Empty_Value_Type</rng:choice>
	</rng:define>	
	<!--
		Integer Value
	-->
	<rng:define name="Integer_Value_Type">
		<a:documentation>
			integer + Unspecified and Unknown
		</a:documentation>
		<rng:choice>
<rng:data type="unsignedInt">xsd:unsignedInt imdi:Empty_Value_Type</rng:data>
<rng:ref name="Empty_Value_Type"/>xsd:unsignedInt imdi:Empty_Value_Type</rng:choice>
	</rng:define>
	<!-- 
		Date Value
		For future versions: A date field should never be empty, only Unknown or Unspecified
	-->
	<rng:define name="Date_Value_Type">
		<a:documentation>
			Defines a date that can also be empty or Unknown or Unspecified
		</a:documentation>
		<rng:choice>
<rng:ref name="DateRange_Value_Type"/>imdi:DateRange_Value_Type imdi:EmptyString_Value_Type imdi:Empty_Value_Type<rng:ref name="EmptyString_Value_Type"/>imdi:DateRange_Value_Type imdi:EmptyString_Value_Type imdi:Empty_Value_Type<rng:ref name="Empty_Value_Type"/>imdi:DateRange_Value_Type imdi:EmptyString_Value_Type imdi:Empty_Value_Type</rng:choice>
	</rng:define>
	<!-- 
		Date Range Value
	-->
	<rng:define name="DateRange_Value_Type">
		<a:documentation>
			Defines a date range that can also be Unspecified or Unknown
		</a:documentation>
		<rng:data type="string">
			<rng:param name="pattern">([0-9]+)((-[0-9]+)(-[0-9]+)?)?(/([0-9]+)((-[0-9]+)(-[0-9]+)?)?)?|Unknown|Unspecified</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		LanguageId Value
	-->
	<rng:define name="LanguageId_Value_Type">
		<a:documentation>
			Language identifiers
		</a:documentation>
		<rng:data type="token">
			<rng:param name="pattern">(ISO639(-1|-2|-3)?:.*)?</rng:param>
			<rng:param name="pattern">(RFC3066:.*)?</rng:param>
			<rng:param name="pattern">(RFC1766:.*)?</rng:param>
			<rng:param name="pattern">(SIL:.*)?</rng:param>
			<rng:param name="pattern">Unknown</rng:param>
			<rng:param name="pattern">Unspecified</rng:param>
		</rng:data>
	</rng:define>
	<!--
		TimePosition Value
	-->
	<rng:define name="TimePosition_Value_Type">
		<a:documentation>
			Time position in the hh:mm:ss:ff format
		</a:documentation>
		<rng:data type="string">
			<rng:param name="pattern">[0-9][0-9]:[0-9][0-9]:[0-9][0-9]:?[0-9]*|Unknown|Unspecified</rng:param>
		</rng:data>
	</rng:define>
	<!-- 
		Quality Value
	-->
	<rng:define name="Quality_Value_Type">
		<a:documentation>
			Quality values (1 .. 5) also allows empty values
		</a:documentation>
		<rng:choice>
			
				<rng:choice>
					<rng:value>1</rng:value>
					<rng:value>2</rng:value>
					<rng:value>3</rng:value>
					<rng:value>4</rng:value>
					<rng:value>5</rng:value>
				</rng:choice>
			
			
				<rng:ref name="Empty_Value_Type"/>
			
		</rng:choice>
	</rng:define>
	<!-- 
		Vocabulary Type Value
	-->
	<rng:define name="VocabularyType_Value_Type">
		<a:documentation>
			All possible vocabulary type values
		</a:documentation>
		<rng:choice>
			<rng:value>ClosedVocabulary</rng:value>
			<rng:value>ClosedVocabularyList</rng:value>
			<rng:value>OpenVocabulary</rng:value>
			<rng:value>OpenVocabularyList</rng:value>
		</rng:choice>
	</rng:define>
	<!-- 
		Link Value
	-->
	<rng:define name="Link_Value_Type">
		<rng:data type="anyURI"/>
	</rng:define>
	<!--
		Metatranscript Value
	-->
	<rng:define name="Metatranscript_Value_Type">
		<a:documentation>
			Allowed values for metadata transcripts
		</a:documentation>
		<rng:choice>
			<rng:value>SESSION</rng:value>
			<rng:value>SESSION.Profile</rng:value>
			<rng:value>LEXICON_RESOURCE_BUNDLE</rng:value>
			<rng:value>LEXICON_RESOURCE_BUNDLE.Profile</rng:value>
			<rng:value>CATALOGUE</rng:value>
			<rng:value>CATALOGUE.Profile</rng:value>
			<rng:value>CORPUS</rng:value>
			<rng:value>CORPUS.Profile</rng:value>
		</rng:choice>
	</rng:define>
	<!-- 
		Special attributes for profiles
	-->
	<rng:define name="ProfileAttributes">
		<a:documentation>
			Attributes allowed for profiles
		</a:documentation>
		<rng:optional>
<rng:attribute name="XXX-Type">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="XXX-Multiple">
<rng:data type="boolean"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="XXX-Visible">
<rng:data type="boolean"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="XXX-Tag">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="XXX-HelpText">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
		<rng:optional>
<rng:attribute name="XXX-FollowUpDepend">
<rng:data type="string"/>
</rng:attribute>
</rng:optional>
	</rng:define>
</rng:grammar>
"""
