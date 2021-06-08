# Introduction
In order to create a consistent style, we need to follow some coding conventions which has been set as follows based on experience and references from other github repos where thousands collaborate to create a project of grand scale.

# Styles to be followed for all
We will
* avoid coding long lines, the maximum we move to in a line of code is **80**, but sometimes moving upto 90 based on scenarios is fine.

# HTML Styling
We would like to write consistent, clean and tidy HTML code. So, we need to follow these coding conventions strictly.

## Always Declaring Document Type
Always declaring document type at the top of the document as:
```
<!DOCTYPE html>
```

## Using Lowercase Element Names
We will use lowercase naming like:
```
<body>
<p>this is a paragraph</p>
</body>
```
not:
```
<BODY>
<P>this is a paragraph</P>
</BODY>
```

## Closing All HTML Elements
We will close all html elements, even single tagged functions like `<img />`, `<br />` and not like `<img>` and `<br>` etc.

## Using Lowercase Attribute Names
We will use lower case attributes name like `<a href="http://somewhere.com">Somewhere</a>` and not `<a HREF="http://somewhere.com">Somewhere</a>`.

## Using Quoted Attributes
We will use quoted attributes as `<table class="striped"></table>` and not `<table class=striped></table>`.

## In An Image
We will always specify the `src` and `alt` as `<img src="something.jpg" alt="Something">`

## Spaces And Equal Signs
We will NOT use spaces like this `<link rel = "stylesheet" href = "styles.css">`, instead we will do this `<link rel="stylesheet" href="styles.css">`.

## Avoiding Excessive Usage Of Spaces
We will group related elements and place spaces between them but not keep spaces between inside the related element like:
```
<body>

<h1>Famous Cities</h1>

<h2>Tokyo</h2>
<p>Tokyo is the capital of Japan, the center of the Greater Tokyo Area,
and the most populous metropolitan area in the world.
It is the seat of the Japanese government and the Imperial Palace,
and the home of the Japanese Imperial Family.</p>

</body>
```
and not:
```
<body>

  <h1>Famous Cities</h1>

  <h2>Tokyo</h2>

  <p>
    Tokyo is the capital of Japan, the center of the Greater Tokyo Area,
    and the most populous metropolitan area in the world.
    It is the seat of the Japanese government and the Imperial Palace,
    and the home of the Japanese Imperial Family.
  </p>

</body>
```
### A Good Table Example
```
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>A</td>
    <td>Description of A</td>
  </tr>
  <tr>
    <td>B</td>
    <td>Description of B</td>
  </tr>
</table>
```
### A Good List Example
```
<ul>
  <li>London</li>
  <li>Paris</li>
  <li>Tokyo</li>
</ul>
```
## Never Omitting These
We will NEVER OMIT `<title>`, `<head>`, `<body>` elements.

## Adding Lang Attribute
We will add lang attributes to HTML element as `<html lang="en-US"></html>`.

## Adding Meta Data
We will add required `<meta>` data as:
* 
so that our web application is deployable and searchable if we deploy it later on.
